# -*- coding: utf-8 -*-

import time
from openerp.report import report_sxw
from osv import orm, osv, fields
from openerp.addons.jasper_reports.pytils import numeral

class torg_form(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(torg_form, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {'time': time,})

report_sxw.report_sxw('report.new_torg_form_report', 'account.invoice',
                      'torg_print_form/torg12.jrxml',
                      parser=torg_form)

class account_invoice(osv.osv):

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

    _name = 'account.invoice'
    _inherit = 'account.invoice'
    _columns = {
        'price_in_words': fields.function(_get_price_in_words, type='char'),
        'pos_in_words': fields.function(_get_pos_in_words, type='char'),
        'invoices_count': fields.function(_get_invoices_count, type='integer'),
    }
account_invoice()

class product_uom(osv.osv):
    _name = 'product.uom'
    _inherit = 'product.uom'
    _columns = {
        'OKEI': fields.integer('Код по ОКЕИ'),
    }
product_uom()

class invoice_line(osv.osv):
    def _get_line_tax(self,cr,uid,ids,field,arg,context=None):
        res = {}

        for row in self.browse(cr, uid, ids, context):
            #invoice_line/invoice_line_tax_id/amount
            res[row.id] = 0

            for line in row.invoice_line_tax_id:
                res[row.id] += line.amount

            #print row.invoice_line.tax
        print res
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

        print '\n\n', res, '\n\n'
        return res

    _name = 'account.invoice.line'
    _inherit = 'account.invoice.line'
    _columns = {
        'line_tax_amount': fields.function(_get_line_tax, type='double'),
        'line_tax_total': fields.function(_get_tax_total, type='double'),
        'line_taxed_subtotal': fields.function(_get_taxed_subtotal, type='double'),
    }