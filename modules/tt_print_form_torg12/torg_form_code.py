# -*- coding: utf-8 -*-

import time
from openerp.report import report_sxw
from openerp.osv import orm, osv, fields
from openerp.addons.jasper_reports.pytils import numeral
from tools.translate import _

class torg_form(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(torg_form, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {'time': time,})

report_sxw.report_sxw('report.new_torg_form_report', 'account.invoice',
                      'tt_print_form_torg12/torg12.jrxml',
                      parser=torg_form)

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

    def _get_pos_in_words(self,cr,uid,ids,field,arg,context=None):
        res = {}

        for row in self.browse(cr, uid, ids, context):
            res[row.id] = numeral.in_words(len(row.invoice_line))

        return res

    def _get_price_in_words(self,cr,uid,ids,field,arg,context=None):
        res = {}

        for row in self.browse(cr, uid, ids, context):
            rubles = numeral.rubles(int(row.amount_total))
            copek_tmp = round(row.amount_total - int(row.amount_total))
            copek = numeral.choose_plural(int(copek_tmp), (u"копейка", u"копейки", u"копеек"))
            res[row.id] = ("%s %02d %s")%(rubles, copek_tmp, copek)

        return res

    def _get_invoices_count(self,cr,uid,ids,field,arg,context=None):
        res = {}

        for row in self.browse(cr, uid, ids, context):
            res[row.id] = len(row.invoice_line)

        return res

    def _weight_nett_in_words(self, cr, uid, ids, field, arg, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context):
            weight = 0

            for line in invoice.invoice_line:
                if line.product_id.weight_net:
                    weight += line.product_id.weight_net*line.quantity

            if weight:
                res[invoice.id] = numeral.in_words(weight)
            else:
                res[invoice.id] = ""
        return res

    def _weight_brutt_in_words(self, cr, uid, ids, field, arg, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context):
            weight = 0
            for line in invoice.invoice_line:
                if line.product_id.weight:
                    weight += line.product_id.weight*line.quantity
            if weight:
                res[invoice.id] = numeral.in_words(weight)
            else:
                res[invoice.id] = ""
        return res

    def _get_origin_number(self, cr, uid, ids, fields, arg, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context):
            if invoice.partner_id.contract_num and invoice.partner_id.contract_date:
                res[invoice.id] = invoice.partner_id.contract_num
            elif invoice.origin:
                so_obj = self.pool.get('sale.order')
                order_id = so_obj.search(cr, uid, [('name', '=', invoice.origin)], context=context)[0]
                order = so_obj.browse(cr, uid, order_id, context=context)

                seq_id = self.pool.get('ir.sequence').search(cr, uid, [('code', '=', 'sale.order')])
                sequence = self.pool.get('ir.sequence').read(cr, uid, seq_id, ['padding', 'active'])[0]
                if sequence and sequence.get('active'):
                    padding = sequence.get('padding')
                    padding = 0 - int(padding)
                    res[invoice.id] = order.name[padding:].lstrip('0')
                else:
                    res[invoice.id] = ""
            else:
                res[invoice.id] = ""
        return res

    def _get_origin_date(self, cr, uid, ids, fields, arg, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context):
            if invoice.partner_id.contract_date and invoice.partner_id.contract_num:
                res[invoice.id] = invoice.partner_id.contract_date
            elif invoice.origin:
                so_obj = self.pool.get('sale.order')
                order_id = so_obj.search(cr, uid, [('name', '=', invoice.origin)], context=context)[0]
                res[invoice.id] = so_obj.browse(cr, uid, order_id, context=context).date_order
            else:
                res[invoice.id] = ""
        return res

    def _get_origin_type(self, cr, uid, ids, fields, arg, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context):
            if invoice.partner_id.contract_num:
                res[invoice.id] = "Договор"
            elif invoice.origin:
                res[invoice.id] = "Заказ"
            else:
                res[invoice.id] = ""
        return res

    _name = 'account.invoice'
    _inherit = 'account.invoice'
    _columns = {
        'number_only': fields.function(_get_number_only, type='char'),
        'price_in_words': fields.function(_get_price_in_words, type='char'),
        'pos_in_words': fields.function(_get_pos_in_words, type='char'),
        'invoices_count': fields.function(_get_invoices_count, type='integer'),
        'weight_nett_in_words': fields.function(_weight_nett_in_words, type='char', store=False),
        'weight_brutt_in_words': fields.function(_weight_brutt_in_words, type='char', store=False),
        'origin_number': fields.function(_get_origin_number, type='char', store=False),
        'origin_date': fields.function(_get_origin_date, type='date', store=False),
        'origin_type': fields.function(_get_origin_type, type='char', store=False),
    }
account_invoice()


class invoice_line(osv.osv):
    def _get_line_tax(self,cr,uid,ids,field,arg,context=None):
        res = {}

        for row in self.browse(cr, uid, ids, context):
            res[row.id] = 0

            for line in row.invoice_line_tax_id:
                res[row.id] += line.amount

        return res

    def _get_tax_total(self,cr,uid,ids,field,arg,context=None):
        res = {}

        for row in self.browse(cr, uid, ids, context):
            res[row.id] = row.line_tax_amount * row.price_subtotal

        return res

    def _get_taxed_subtotal(self,cr,uid,ids,field,arg,context=None):
        res = {}

        for row in self.browse(cr, uid, ids, context):
            res[row.id] = row.line_tax_total + row.price_subtotal

        return res

    _name = 'account.invoice.line'
    _inherit = 'account.invoice.line'
    _columns = {
        'line_tax_amount': fields.function(_get_line_tax, type='double'),
        'line_tax_total': fields.function(_get_tax_total, type='double'),
        'line_taxed_subtotal': fields.function(_get_taxed_subtotal, type='double'),
    }