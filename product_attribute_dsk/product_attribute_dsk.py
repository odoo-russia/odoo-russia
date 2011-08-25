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

class product_attribute_group(osv.osv):
    _name = 'product.attribute.group'
    _columns = {
        'name': fields.char('Product attribute group name', size=64, required=True),
        'attribute_ids': fields.many2many(
            'product.attribute',
            'product_attribute_group_attribute',
            'attribute_group_id',
            'attribute_id',
            'Attributes'),
    }
    _sql_constraints = [('attribute_group_name_unique','unique(name)','Attribute group name must be unique!')]
product_attribute_group()

class product_attribute(osv.osv):
    _name = 'product.attribute'
    _columns = {
        'name': fields.char('Product attribute name', size=64, required=True),
        'attribute_value_ids': fields.one2many('product.attribute.value','attribute_id','Attribute values'),
        'attribute_group_ids': fields.many2many(
            'product.attribute.group',
            'product_attribute_group_attribute',
            'attribute_id',
            'attribute_group_id',
            'Attribute groups'),
    }
    _sql_constraints = [('attribute_name_unique','unique(name)','Attribute name must be unique!')]
product_attribute()

class product_attribute_value(osv.osv):
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        attribute_id = context.get('attribute_id')
        if attribute_id:
            vals['attribute_id']=attribute_id
        return super(product_attribute_value, self).create(cr, uid, vals, context)

    _name = 'product.attribute.value'
    _columns = {
        'name': fields.char('Product attribute value', size=64, required=True),
        'attribute_id': fields.many2one('product.attribute', 'Product attribute', ondelete='restrict', required=True),
    }

    _sql_constraints = [('attribute_name_value_unique','unique(attribute_id, name)','Attribute value must be unique!')]
product_attribute_value()

class product_attribute_value_product(osv.osv):
    def _check_attribute_group_relation(self, cr, uid, ids):
        for product_avp in self.browse(cr, uid, ids):
            print (product_avp.attribute_group_id, product_avp.attribute_group_ids)
            if product_avp.attribute_group_id not in product_avp.attribute_group_ids: return False
        return True

    def _check_attribute_value_relation(self, cr, uid, ids):
        for product_avp in self.browse(cr, uid, ids):
            print (product_avp.attribute_id, product_avp.attribute_value_attribute_id)
            if product_avp.attribute_id != product_avp.attribute_value_attribute_id: return False
        return True

    _name = 'product.attribute.value.product'
    _columns = {
        'attribute_id': fields.many2one('product.attribute', 'Product attribute', ondelete='restrict', required=True),
        'attribute_group_ids': fields.related('attribute_id', 'attribute_group_ids', type='many2many', relation='product.attribute', string='Attribute groups', store=False),
        'attribute_value_id': fields.many2one('product.attribute.value', 'Product attribute value', ondelete='restrict', required=True),
        'attribute_value_attribute_id': fields.related('attribute_value_id', 'attribute_id', type='many2one', relation='product.attribute.value', string="Attribute value parent id", store=False),
        'product_id': fields.many2one('product.product', 'Product', ondelete='cascade', required=True),
        'attribute_group_id': fields.related('product_id', 'attribute_group', type='many2one', relation='product.product', str='Attribute group', store=False),
    }
    _sql_constraints = [('attribute_name_product_unique','unique(attribute_id, product_id)','Attribute name must be unique!')]
    _constraints = [
        (_check_attribute_group_relation, 'Mismatch in attribute group!', ['attribute_id', 'attribute_value_id']),
        (_check_attribute_value_relation, 'Mismatch in attribute value!', ['attribute_id', 'attribute_value_id'])
    ]
product_attribute_value_product()

class product_product(osv.osv):
    def onchange_attribute_group(self, cr, uid, ids, attribute_group):
        v = {'attribute_value_product_ids': []}

        return {'value': v}

    _name = 'product.product'
    _inherit = 'product.product'
    _columns = {
        'attribute_group': fields.many2one('product.attribute.group','Product attribute group', ondelete='restrict', select=True),
        'attribute_value_product_ids': fields.one2many('product.attribute.value.product', 'product_id', 'Attributes and their values'),
    }
product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: