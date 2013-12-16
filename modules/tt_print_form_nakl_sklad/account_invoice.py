# -*- coding: utf-8 -*-
from openerp.osv import osv, fields


class account_invoice(osv.osv):
    def _get_number_only(self, cr, uid, ids, field_name, arg, context):
        res = {}
        seq_obj = self.pool.get('ir.sequence')

        for row in self.browse(cr, uid, ids, context):
            number = u'0-черновик'
            seq_id = seq_obj.search(cr, uid, ['|', ('code', '=', self._name),
                                              ('name', '=', 'Account Default Sales Journal')], context=context)
            seq_id = seq_id and seq_id[0] or False

            if seq_id and row.number:
                seq_data = seq_obj.read(cr, uid, seq_id, ['padding'], context=context)
                padding = seq_data.get('padding')
                padding = 0 - int(padding)
                number = row.number[padding:].lstrip('0')
            res[row.id] = number
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

