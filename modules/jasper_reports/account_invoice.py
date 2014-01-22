#coding: utf-8
#from osv import fields, osv
from openerp.osv import orm, osv, fields

class account_invoice(osv.osv):
    # def _get_date_order(self,cr,uid,ids,field,arg,context=None):
    #     res = {}
    #     for row in self.browse(cr, uid, ids, context):
    #         res[row.id] = row.date_invoice
    #         return res
    #
    # def _get_invoice_line(self,cr,uid,ids,field,arg,context=None):
    #     res = {}
    #     for row in self.browse(cr, uid, ids, context):
    #         res[row.id] = row.invoice_line
    #
    #     return res
    #
    # def _get_line(self,cr,uid,ids,field,arg,context=None):
    #     res = {}
    #     for row in self.browse(cr, uid, ids, context):
    #         res[row.id] = row.invoice_line
    #     return res
    #
    # def _get_partner_shipping_id(self,cr,uid,ids,field,arg,context=None):
    #     res = {}
    #     sale_order = self.pool.get('sale.order')
    #
    #     for row in self.browse(cr,uid, ids, context):
    #         id = sale_order.search(cr, uid, [('name', '=', row.origin), ])
    #         res[row.id] = id and id[0] or False
    #
    #     return res

    def _is_invoice(self,cr,uid,ids,field,arg,context=None):
        res = {}

        for row in self.browse(cr, uid, ids, context):
            res[row.id] = "True"

        return res

    _name = 'account.invoice'
    _inherit = 'account.invoice'
    _columns = {
        # 'date_order': fields.function(_get_date_order, 'date'),
        # 'order_line': fields.function(_get_invoice_line, 'one2many'),
        # 'line': fields.function(_get_line, 'one2many'),
        # 'partner_shipping_id': fields.function(_get_partner_shipping_id, 'many2one'),
        'isInvoice': fields.function(_is_invoice, type='char'),

    }
account_invoice()
