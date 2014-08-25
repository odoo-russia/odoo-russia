# -*- coding: utf-8 -*-

import time
from openerp.report import report_sxw
from osv import orm, osv, fields
from openerp.tools.translate import _


class bill_of_product_report(report_sxw.rml_parse):
    name = 'account_invoice.new_bill_report'

    def __init__(self, cr, uid, name, context):
        super(bill_of_product_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time})

report_sxw.report_sxw('report.new_bill_of_product_report', 'account_invoice',
                      'tt_print_form_nakl_sklad/bill_of_product.jrxml',
                      parser=bill_of_product_report)


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

    def _get_invoices_count(self, cr, uid, ids, field, arg, context=None):
        res = {}

        for row in self.browse(cr, uid, ids, context):
            res[row.id] = len(row.invoice_line)

        return res

    _name = 'account.invoice'
    _inherit = 'account.invoice'
    _columns = {
        'number_only': fields.function(_get_number_only, type='char'),
        'invoices_count': fields.function(_get_invoices_count, type='integer'),
    }
account_invoice()
