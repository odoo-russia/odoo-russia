# -*- coding: utf-8 -*-

import time
from openerp.report import report_sxw
from osv import orm, osv, fields


class sale_order_report(report_sxw.rml_parse):
    name = 'sale.order.new_report'
    def __init__(self, cr, uid, name, context):
        super(sale_order_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {'time': time,})

report_sxw.report_sxw('report.new_sale_order_report', 'sale.order',
                      'sale_order_print_form/Schet.jrxml',
                      parser=sale_order_report)


class account_invoice_report(report_sxw.rml_parse):
    name = 'account_invoice.new_report'
    def __init__(self, cr, uid, name, context):
        super(account_invoice_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {'time': time,})

report_sxw.report_sxw('report.new_account_invoice_report', 'account_invoice',
                      'sale_order_print_form/Schet.jrxml',
                      parser=account_invoice_report)


class sale_order(osv.osv):
    def _is_invoice(self,cr,uid,ids,field,arg,context=None):
        res = {}
        for row in self.browse(cr, uid, ids, context):
            res[row.id] = False
        return res

    _name = 'sale.order'
    _inherit = 'sale.order'
    _columns = {
        'is_invoice': fields.function(_is_invoice, type='boolean'),
    }
sale_order()


class account_invoice(osv.osv):
    def _is_invoice(self,cr,uid,ids,field,arg,context=None):
        res = {}
        for row in self.browse(cr, uid, ids, context):
            res[row.id] = True
        return res

    _name = 'account.invoice'
    _inherit = 'account.invoice'
    _columns = {
        'is_invoice': fields.function(_is_invoice, type='boolean'),
    }
account_invoice()
