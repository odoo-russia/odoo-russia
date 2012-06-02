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
from tools.translate import _

class product_attribute_group(osv.osv):
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if 'name' in vals:
            vals['name'] = vals['name'].capitalize()
        return super(product_attribute_group, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if 'name' in vals:
            vals['name'] = vals['name'].capitalize()
        #Protection from deleting links between groups of product's attributes and product's attributes.
        #It's needed because product's attributes may have values with links to groups of product's attributes.
        if 'attribute_ids' in vals:
            attribute_value_references={}
            for attribute_ids_act in vals['attribute_ids']:
                if attribute_ids_act[0] == 6:
                    for attribute_group in self.browse(cr, uid, ids, context):
                        linked_attribute_value_ids = self.pool.get('product.attribute.value').search(cr, uid,
                                                    [('attribute_group_id', '=', attribute_group.id)], context=context)
                        for linked_attribute_value in self.pool.get('product.attribute.value').browse(cr, uid,
                                                                                linked_attribute_value_ids, context):
                            if linked_attribute_value.attribute_id.id not in attribute_ids_act[2]:
                                linked_attribute_id = linked_attribute_value.attribute_id.id
                                if linked_attribute_id in attribute_value_references:
                                    attribute_value_references[linked_attribute_id]['items'].append(linked_attribute_value.name)
                                else:
                                    attribute_value_references[linked_attribute_id] = {
                                        'name': linked_attribute_value.attribute_id.name,
                                        'items': [linked_attribute_value.name,],
                                    }
            if attribute_value_references:
                attribute_value_references_str = ''
                for attribute_value_reference in attribute_value_references.values():
                    attribute_values_str = ', '.join(attribute_value_reference['items'])
                    attribute_value_reference_str = ': '.join((attribute_value_reference['name'], attribute_values_str))
                    if attribute_value_references_str:
                        attribute_value_references_str = '\r\n'.join((attribute_value_references_str, attribute_value_reference_str))
                    else:
                        attribute_value_references_str = attribute_value_reference_str
                raise osv.except_osv(_('There is several product attribute values with links to this product attribute \
                                        group.'), _('First remove these references: ') + attribute_value_references_str)
        return super(product_attribute_group, self).write(cr, uid, ids, vals, context)

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for attribute_group in self.browse(cr, uid, ids, context):
            attribute = self.pool.get('product.attribute')
            attribute_ids = attribute.search(cr, uid, [('attribute_group_ids', 'in', attribute_group.id),])
            if attribute_ids:
                attribute_names = []
                for attribute_element in attribute.browse(cr, uid, attribute_ids):
                    attribute_names.append(attribute_element.name)
                attribute_names_str = ', '.join(attribute_names)
                raise osv.except_osv(_('Some attributes have references to the attribute group ') + attribute_group.name +
                                     '!', _('First remove these references: ') + attribute_names_str)
        return super(product_attribute_group, self).unlink(cr, uid, ids)

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
        if 'name' in vals and len(vals['name']) > 1:
            vals['name'] = vals['name'][0].upper() + vals['name'][1:]
        return super(product_attribute, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if 'name' in vals and len(vals['name']) > 1:
            vals['name'] = vals['name'][0].upper() + vals['name'][1:]

        for attribute in self.browse(cr, uid, ids, context):
            if attribute.attribute_value_ids:
                vals['type']='string'
        return super(product_attribute, self).write(cr, uid, ids, vals, context)

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for attribute in self.browse(cr, uid, ids, context):
            attribute_group = self.pool.get('product.attribute.group')
            attribute_group_ids = attribute_group.search(cr, uid, [('attribute_ids', 'in', attribute.id),])
            if attribute_group_ids:
                attribute_group_names = []
                for attribute_group_element in attribute_group.browse(cr, uid, attribute_group_ids):
                    attribute_group_names.append(attribute_group_element.name)
                attribute_group_names_str = ', '.join(attribute_group_names)
                raise osv.except_osv(_('Some attribute groups have references to the attribute ') + attribute.name + '!',
                                     _('First remove these  references: ') + attribute_group_names_str)
        return super(product_attribute, self).unlink(cr, uid, ids)

    def _get_parent_group_id(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        res = {}
        attribute_group_id = context.get('attribute_group_id')
        for attribute in self.browse(cr, uid, ids, context):
            if attribute_group_id:
                res[attribute.id] = attribute_group_id
            else:
                res[attribute.id] = 0
        return res

    _name = 'product.attribute'
    _columns = {
        'name': fields.char('Product attribute name', size=64, required=True),
        'type': fields.selection(
            (('string', 'String'), ('checkbox', 'Checkbox')),
            'Attribute type',
            required=True),
        'attribute_group_ids': fields.many2many(
            'product.attribute.group',
            'product_attribute_group_attribute',
            'attribute_id',
            'attribute_group_id',
            'Attribute groups'),
        'attribute_parent_group_id': fields.function(_get_parent_group_id, 'For context transfer', type='integer', method=True, store=False),
        'attribute_value_ids': fields.one2many('product.attribute.value', 'attribute_id', 'Attribute values'),
    }
    _defaults = {
        'type': lambda *a: 'string',
    }
    _order = 'type'
    _sql_constraints = [('attribute_name_unique','unique(name)','Attribute name must be unique!')]
product_attribute()

class product_attribute_value(osv.osv):
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if 'name' in vals and len(vals['name']) > 1:
            vals['name'] = vals['name'][0].upper() + vals['name'][1:]
        return super(product_attribute_value, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if 'name' in vals and len(vals['name']) > 1:
            vals['name'] = vals['name'][0].upper() + vals['name'][1:]
        return super(product_attribute_value, self).write(cr, uid, ids, vals, context)

    _name = 'product.attribute.value'
    _columns = {
        'name': fields.char('Product attribute value name', size=64, required=True),
        'attribute_id': fields.many2one('product.attribute', 'Attribute', required=True, ondelete='restrict'),
        'attribute_group_id': fields.many2one('product.attribute.group', 'Attribute group', required=True,
                                              ondelete='restrict'),
    }
    _order = 'attribute_group_id'
    _sql_constraints = [('name_attribute_group_unique', 'unique(name, attribute_id, attribute_group_id)',
                         'Attribute value must be unique!')]
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
        'attribute_value_id': fields.many2one('product.attribute.value', 'Product attribute value', ondelete='restrict'),
        'checkbx_value': fields.boolean('Checkbox value'),
        'product_id': fields.many2one('product.product', 'Product', ondelete='cascade', required=True),
    }
    _sql_constraints = [('attribute_name_product_unique','unique(attribute_id, product_id)','Attribute name must be unique!')]
    _constraints = [(_check_references, "Value don't belong to selected attribute!", ['attribute_value_id'])]
product_attribute_value_product()

class product_product(osv.osv):
    def _check_references(self, cr, uid, ids):
        for product in self.browse(cr, uid, ids):
            for product_avp in product.attribute_value_product_ids:
                if product.attribute_group not in product_avp.attribute_id.attribute_group_ids or \
                   product.attribute_group != product_avp.attribute_value_id.attribute_group_id:
                    return False
        return True

    _name = 'product.product'
    _inherit = 'product.product'
    _columns = {
        'attribute_group': fields.many2one('product.attribute.group','Product attribute group', ondelete='restrict', select=True),
        'attribute_value_product_ids': fields.one2many('product.attribute.value.product', 'product_id',
            'Attributes and their values', domain=[('attribute_id.type', '=', 'string')]),
        'attribute_value_product_checkbx_ids': fields.one2many('product.attribute.value.product', 'product_id',
            'Attributes and theis values-checkboxes', domain=[('attribute_id.type', '=', 'checkbox')]),
        }
    _constraints = [(_check_references,'Attributes or attribute values don\'t belong to selected group!',['attribute_group'])]
product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: