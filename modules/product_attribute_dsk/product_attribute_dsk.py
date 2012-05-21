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
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        name = vals.get('name')
        if name:
            for attribute_group in self.browse(cr, uid, ids, context):
                
            samename_ids = pool.get('product.attribute.group').search(cr, uid, [('name.lower()', '=', name.lower())], context=context)
            print samename_ids
        else:
            print 'fuck'

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
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        attribute_group_id = context.get('attribute_group_id')
        if attribute_group_id:
            vals['attribute_group_ids']=[(4, attribute_group_id)]
        type = context.get('attribute_type');
        if type:
            vals['type']=type;
        return super(product_attribute, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        for attribute in self.browse(cr, uid, ids, context):
            if attribute.attribute_value_ids:
                vals['type']='string'
        return super(product_attribute, self).write(cr, uid, ids, vals, context)

    def _get_parent_group_id(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        res = {}
        attribute_group_id = context.get('attribute_group_id')
        if attribute_group_id:
            for attribute in self.browse(cr, uid, ids, context):
                res[attribute.id] = attribute_group_id
        return res

    _name = 'product.attribute'
    _columns = {
        'name': fields.char('Product attribute name', size=64, required=True),
        'type': fields.selection(
            (('string', 'String'), ('checkbox', 'Checkbox')),
            'Attribute type',
            required=True),
        'attribute_value_ids': fields.one2many('product.attribute.value','attribute_id','Attribute values'),
        'attribute_group_ids': fields.many2many(
            'product.attribute.group',
            'product_attribute_group_attribute',
            'attribute_id',
            'attribute_group_id',
            'Attribute groups'),
        'attribute_parent_group_id': fields.function(_get_parent_group_id, 'For context transfer', type='integer', method=True, store=False),
    }
    _order = 'type'
    _sql_constraints = [('attribute_name_unique','unique(name)','Attribute name must be unique!')]
product_attribute()

class product_attribute_value(osv.osv):
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        attribute_id = context.get('attribute_id')
        attribute_group_id = context.get('attribute_group_id')
        if attribute_id:
            vals['attribute_id'] = attribute_id
        if attribute_group_id:
            vals['attribute_group_id'] = attribute_group_id
        return super(product_attribute_value, self).create(cr, uid, vals, context)

    def search(self, cr, uid, ids, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        attribute_group_id = context.get('attribute_group_id')
        if attribute_group_id:
            ids.append(('attribute_group_id','=',attribute_group_id))
        return super(product_attribute_value, self).search(cr, uid, ids, limit=limit, order=order, context=context,
                                                           count=count)
    
    _name = 'product.attribute.value'
    _columns = {
        'name': fields.char('Product attribute value', size=64, required=True),
        'attribute_id': fields.many2one('product.attribute', 'Product attribute', ondelete='cascade', required=True),
        'attribute_group_id': fields.many2one('product.attribute.group', 'Product attribute group', ondelete='restrict',
                                              required=True)
    }
    _sql_constraints = [('attribute_group_name_value_unique','unique(attribute_group_id, attribute_id, name)','Attribute value must be unique!')]
product_attribute_value()

class product_attribute_value_product(osv.osv):
    def onchange_attribute_id(self, cr, uid, ids, attribute_id, attribute_value_id):
        return {'value': {'attribute_value_id': False}}

    def _check_references(self, cr, uid, ids):
        for avp in self.browse(cr, uid, ids):
            if avp.attribute_value_id and avp.attribute_value_id.attribute_id != avp.attribute_id:
                return False
        return True

    _name = 'product.attribute.value.product'
    _columns = {
        'name': fields.char('', size=64),
        'attribute_id': fields.many2one('product.attribute', 'Product attribute', ondelete='restrict', required=True),
        'checkbx_value': fields.boolean('Checkbox value'),
        'attribute_value_id': fields.many2one('product.attribute.value', 'Product attribute value', ondelete='restrict'),
        'product_id': fields.many2one('product.product', 'Product', ondelete='cascade', required=True),
    }
    _sql_constraints = [('attribute_name_product_unique','unique(attribute_id, product_id)','Attribute name must be unique!')]
    _constraints = [(_check_references, "Value don't belong to selected attribute!", ['attribute_value_id'])]
product_attribute_value_product()

class product_product(osv.osv):
    def _check_references(self, cr, uid, ids):
        for product in self.browse(cr, uid, ids):
            for product_avp in product.attribute_value_product_ids:
                if product.attribute_group not in product_avp.attribute_id.attribute_group_ids:
                    return False
        return True

    _name = 'product.product'
    _inherit = 'product.product'
    _columns = {
        'attribute_group': fields.many2one('product.attribute.group','Product attribute group', ondelete='restrict', select=True),
        'attribute_value_product_ids': fields.one2many('product.attribute.value.product', 'product_id', 'Attributes and their values', domain=[('attribute_id.type', '=', 'string')]),
        'attribute_value_product_checkbx_ids': fields.one2many('product.attribute.value.product', 'product_id',
                                                                'Attributes and theis values-checkboxes', domain=[('attribute_id.type', '=', 'checkbox')]),
    }
    _constraints = [(_check_references,'Attributes don\'t belong to selected group!',['attribute_group'])]
product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: