# -*- coding: utf-8 -*-

import time
import logging
from openerp.addons.pad import pad
from openerp.report import report_sxw
from osv import orm, osv, fields

_logger = logging.getLogger(__name__)

###------ Rgister Sale Order Report ----------###
class sale_order_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sale_order_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {'time': time,})

report_sxw.report_sxw('report.sale.order.new_report', 'sale.order',
                      'sale_order_print_form/Schet.jrxml',
                      parser=sale_order_report)


###------ Rgister Account Invoice Report ----------###
class account_invoice_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_invoice_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {'time': time,})

report_sxw.report_sxw('report.new_account_invoice_report', 'account_invoice',
                      'sale_order_print_form/Schet.jrxml',
                      parser=account_invoice_report)


###------ Modify sale order ----------###
###------   + add is_invoice field ---###
###------   + add number_only field --###
class sale_order(osv.osv):
    _name = 'sale.order'
    _inherit = 'sale.order'

    def _is_invoice(self,cr,uid,ids,field,arg,context=None):
        res = {}
        for row in self.browse(cr, uid, ids, context):
            res[row.id] = False
        return res

    # Parse order name. Strip order prefix and leading zeroes
    def _get_number_only(self, cr, uid, ids, field_name, arg, context):
        res = {}

        for row in self.browse(cr, uid, ids, context):
            seq_id = self.pool.get('ir.sequence').search(cr, uid, [('code', '=', 'sale.order')])
            sequence = self.pool.get('ir.sequence').read(cr, uid, seq_id, ['padding', 'active'])[0]
            if sequence and sequence.get('active'):
                padding = sequence.get('padding')
                padding = 0 - int(padding)
                res[row.id] = row.name[padding:].lstrip('0')

        return res

    _columns = {
        'is_invoice': fields.function(_is_invoice, type='boolean'),
        'number_only': fields.function(_get_number_only, type='char'),
    }
sale_order()


class account_invoice(osv.osv):
    def _get_number_only(self, cr, uid, ids, field_name, arg, context):
        res = {}

        for row in self.browse(cr, uid, ids, context):
            if not row.number:
                raise osv.except_osv('Error!', 'You must confirm invoice!')

            seq_id = self.pool.get('ir.sequence').search(cr, uid, [('code', '=', 'sale.order')])
            sequence = self.pool.get('ir.sequence').read(cr, uid, seq_id, ['padding', 'active'])[0]
            if sequence and sequence.get('active'):
                padding = sequence.get('padding')
                padding = 0 - int(padding)
                res[row.id] = row.number[padding:].lstrip('0')

        return res

    def _is_invoice(self,cr,uid,ids,field,arg,context=None):
        res = {}
        for row in self.browse(cr, uid, ids, context):
            res[row.id] = True
        return res

    _name = 'account.invoice'
    _inherit = 'account.invoice'
    _columns = {
        'is_invoice': fields.function(_is_invoice, type='boolean'),
        'number_only': fields.function(_get_number_only, type='char'),
    }
account_invoice()

