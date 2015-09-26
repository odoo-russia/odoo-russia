#coding: utf-8
from openerp.osv import orm, osv, fields

class sale_order(osv.osv):
    def _is_invoice(self,cr,uid,ids,field,arg,context=None):
        res = {}

        for row in self.browse(cr, uid, ids, context):
            res[row.id] = "False"

        return res

    _name = 'sale.order'
    _inherit = 'sale.order'
    _columns = {
        'isInvoice': fields.function(_is_invoice, type='char'),
    }
sale_order()
