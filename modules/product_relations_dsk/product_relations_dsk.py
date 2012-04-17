##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv

class product_relation(osv.osv):
    _name = 'product.relation'
    _rec_name = 'linked_product_id'

    def _check_loop(self, cr, uid, ids):
        for relation in self.browse(cr, uid, ids):
            if relation.product_id == relation.linked_product_id:
                return False
        return True

    _columns = {
        'product_id': fields.many2one('product.product', 'Source product', required=True, ondelete='cascade'),
        'linked_product_id': fields.many2one('product.product', 'Linked product', required=True, ondelete='cascade'),
        'type': fields.selection(
            (('cross_sell', 'Cross-Sell'), ('up_sell', 'Up-Sell'), ('related', 'Related')),
            'Relation type', required=True
        ),
    }

    _defaults = {
        'type': lambda *a: 'related',
    }

    _constraints = [(_check_loop, 'Relation to himself prohibited!', ['product_id', 'linked_product_id'])]

    _sql_constraints = [('relation_unique','unique(product_id, linked_product_id, type)','Relation must be unique!')]

    _order = 'type'
product_relation()

class product_product(osv.osv):
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        #TODO: context doesn't work for saving
        if context.get('is_name_eshop'):
            res = []
            for product in self.browse(cr, uid, ids, context):
                res.append((product['id'], product['name_eshop']))
            return res
        else:
            return super(product_product, self).name_get(cr, uid, ids, context)

    _name = 'product.product'
    _inherit = 'product.product'

    _columns = {
        'relation_ids': fields.one2many(
            'product.relation',
            'product_id',
            'Product relation',
        ),
    }
product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: