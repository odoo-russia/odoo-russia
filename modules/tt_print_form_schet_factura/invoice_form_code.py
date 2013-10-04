# -*- coding: utf-8 -*-

import time
from openerp.report import report_sxw
from openerp.osv import osv, fields
from openerp.addons.jasper_reports.pytils import numeral
from tools.translate import _


class invoice_form(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(invoice_form, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time})

report_sxw.report_sxw('report.new_invoice_form_report', 'account.invoice',
                      'tt_print_form_schet_factura/invoice.jrxml',
                      parser=invoice_form)


class account_invoice(osv.osv):
    def _get_number_only(self, cr, uid, ids, field_name, arg, context):
        res = {}

        for row in self.browse(cr, uid, ids, context):
            if not row.number:
                raise osv.except_osv(_('Error!'), _('You must confirm invoice!'))

            seq_id = self.pool.get('ir.sequence').search(cr, uid, [('code', '=', 'sale.order')])
            sequence = self.pool.get('ir.sequence').read(cr, uid, seq_id, ['padding', 'active'])[0]
            if sequence and sequence.get('active'):
                padding = sequence.get('padding')
                padding = 0 - int(padding)
                res[row.id] = row.number[padding:].lstrip('0')

        return res

    def _get_pos_in_words(self, cr, uid, ids, field, arg, context=None):
        res = {}

        for row in self.browse(cr, uid, ids, context):
            res[row.id] = numeral.in_words(len(row.invoice_line))

        return res

    def _get_price_in_words(self, cr, uid, ids, field, arg, context=None):
        res = {}

        for row in self.browse(cr, uid, ids, context):
            rubles = numeral.rubles(int(row.amount_total))
            copek_tmp = round(row.amount_total - int(row.amount_total))
            copek = numeral.choose_plural(int(copek_tmp), (u"копейка", u"копейки", u"копеек"))
            res[row.id] = ("%s %02d %s")%(rubles, copek_tmp, copek)

        return res

    def _get_invoices_count(self, cr, uid, ids, field, arg, context=None):
        res = {}

        for row in self.browse(cr, uid, ids, context):
            res[row.id] = len(row.invoice_line)

        return res

    def _get_origin(self, cr, uid, origin_str):
        sale_obj = self.pool.get('sale.order')
        sale_ids = sale_obj.search(cr, uid, [('name', '=', origin_str)])
        if sale_ids:
            return sale_obj.browse(cr, uid, sale_ids[0])
        else:
            return None

    def _format_inn_kpp(self, inn, kpp):
        if inn and kpp:
            res = "%s/%s" % (inn, kpp)
        elif inn:
            res = inn
        elif kpp:
            res = kpp
        else:
            res = ""
        return res

    def _format_bank(self, partner):
        return "Bank info"

    def get_partner_info(self, cr, uid, ids, fields=None, args=None, context=None):
        if context is None:
            context = {}
        res = {}
        for i in ids:
            res[i] = {}.fromkeys(fields, "")

        for field in fields:
            for invoice in self.browse(cr, uid, ids, context=context):
                origin = self._get_origin(cr, uid, invoice.origin)
                field_splitted = field.split('_')
                field_prefix = field_splitted[0]
                field_postfix = field_splitted[-1]

                # Get correct partner by the prefix of field name
                if field_prefix == 'invoice' and origin and origin.partner_invoice_id:
                    partner = origin.partner_invoice_id
                elif field_prefix == 'shipping' and origin and origin.partner_shipping_id:
                    partner = origin.partner_shipping_id
                elif field_prefix == 'company':
                    partner = invoice.company_id.partner_id
                elif field_prefix == 'partner':
                    partner = invoice.partner_id
                else:
                    res[invoice.id][field] = ""
                    continue

                # Get information by the postfix of field name
                if field_postfix == 'name':
                    value = partner.name_official if partner.name_official else partner.name
                elif field_postfix == 'address':
                    partner = partner.parent_id if partner.use_parent_address else partner
                    value = partner.address_formatted
                elif field_postfix == 'innkpp':
                    inn = partner.inn if partner.inn else partner.parent_id.inn
                    kpp = partner.kpp if partner.kpp else partner.parent_id.kpp
                    value = self._format_inn_kpp(inn, kpp)
                elif field_postfix == 'bank':
                    partner = partner.parent_id if partner.is_company else partner
                    value = self._format_bank(partner)
                else:
                    method = getattr(self, "_get_" + field_postfix) or False
                    if method:
                        value = method(invoice, partner)
                    else:
                        value = ""
                res[invoice.id][field] = value
        return res

    _name = 'account.invoice'
    _inherit = 'account.invoice'
    _columns = {
        'number_only': fields.function(_get_number_only, type='char'),
        'price_in_words': fields.function(_get_price_in_words, type='char'),
        'pos_in_words': fields.function(_get_pos_in_words, type='char'),
        'invoices_count': fields.function(_get_invoices_count, type='integer'),
        'invoice_partner_name': fields.function(get_partner_info, type='char', store=False, multi='partner_info'),
        'invoice_address': fields.function(get_partner_info, type='char', store=False, multi='partner_info'),
        'invoice_innkpp': fields.function(get_partner_info, type='char', store=False, multi='partner_info'),
        'shipping_partner_name': fields.function(get_partner_info, type='char', store=False, multi='partner_info'),
        'shipping_address': fields.function(get_partner_info, type='char', store=False, multi='partner_info'),
        'company_name': fields.function(get_partner_info, type='char', store=False, multi='partner_info'),
        'company_address': fields.function(get_partner_info, type='char', store=False, multi='partner_info'),
        'company_innkpp': fields.function(get_partner_info, type='char', store=False, multi='partner_info'),
        'partner_name': fields.function(get_partner_info, type='char', store=False, multi='partner_info'),
    }
account_invoice()


class invoice_line(osv.osv):
    def _get_line_tax(self, cr, uid, ids, field, arg, context=None):
        res = {}

        for row in self.browse(cr, uid, ids, context):
            res[row.id] = 0

            for line in row.invoice_line_tax_id:
                res[row.id] += line.amount

        return res

    def _get_tax_total(self, cr, uid, ids, field, arg, context=None):
        res = {}

        for row in self.browse(cr, uid, ids, context):
            res[row.id] = row.line_tax_amount * row.price_subtotal

        return res

    _name = 'account.invoice.line'
    _inherit = 'account.invoice.line'
    _columns = {
        'line_tax_amount': fields.function(_get_line_tax, type='double'),
        'line_tax_total': fields.function(_get_tax_total, type='double'),
    }