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
    _name = 'product.attribute.value'
    _columns = {
        'name': fields.char('Product attribute value', size=64, required=True),
        'attribute_id': fields.many2one('product.attribute', 'Product attribute', ondelete='restrict', required=True),
    }
    _sql_constraints = [('attribute_name_value_unique','unique(attribute_id, name)','Attribute value must be unique!')]
product_attribute_value()

class product_attribute_value_product(osv.osv):
    _name = 'product.attribute.value.product'
    _columns = {
        'attribute_id': fields.many2one('product.attribute', 'Product attribute', ondelete='restrict', required=True),
        'attribute_value_id': fields.many2one('product.attribute.value', 'Product attribute value', ondelete='restrict', required=True),
        'product_id': fields.many2one('product.product', 'Product', ondelete='cascade', required=True),
    }
    _sql_constraints = [('attribute_name_product_unique','unique(attribute_id, product_id)','Attribute name must be unique!')]
product_attribute_value_product()

class product_product(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'
    _columns = {
        'attribute_group': fields.many2one('product.attribute.group','Product attribute group', ondelete='restrict', select=True),
        'attribute_value_product_ids': fields.one2many('product.attribute.value.product', 'product_id', 'Attributes and their values'),
    }
product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: