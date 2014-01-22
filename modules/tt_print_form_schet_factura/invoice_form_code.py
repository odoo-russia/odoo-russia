# -*- coding: utf-8 -*-

import time
from openerp.report import report_sxw
from openerp.osv import osv, fields
#from openerp.addons.jasper_reports.pytils import numeral
from openerp.addons.jasper_reports import numeral
from openerp.tools.translate import _


class invoice_form(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(invoice_form, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time})

#report_sxw.report_sxw('report.new_invoice_form_report', 'account.invoice',
#                      'tt_print_form_schet_factura/invoice.jrxml',
#                      parser=invoice_form)


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

    def get_partner_info(self, cr, uid, ids, fields=None, args=None, context=None):
        return super(account_invoice, self).get_partner_info(cr, uid, ids, fields, args, context)

    _name = 'account.invoice'
    _inherit = 'account.invoice'
    _columns = {
        'number_only': fields.function(_get_number_only, type='char'),
        'price_in_words': fields.function(_get_price_in_words, type='char'),
        'pos_in_words': fields.function(_get_pos_in_words, type='char'),
        'invoices_count': fields.function(_get_invoices_count, type='integer'),
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
