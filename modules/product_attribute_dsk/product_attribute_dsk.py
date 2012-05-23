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
        vals['name'] = vals['name'].capitalize()
        return super(product_attribute_group, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if 'name' in vals:
            vals['name'] = vals['name'].capitalize()
        return super(product_attribute_group, self).write(cr, uid, ids, vals, context)

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for attribute_group in self.browse(cr, uid, ids):
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
        if 'name' in vals and vals['name']:
            vals['name'] = vals['name'][0].upper() + vals['name'][1:]
        return super(product_attribute, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if 'name' in vals and vals['name']:
            vals['name'] = vals['name'][0].upper() + vals['name'][1:]

        for attribute in self.browse(cr, uid, ids, context):
            if attribute.attribute_value_ids:
                vals['type']='string'
        return super(product_attribute, self).write(cr, uid, ids, vals, context)

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for attribute in self.browse(cr, uid, ids):
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
        attribute_group_id = context.get('attribute_group_id')
        if attribute_group_id:
            vals['attribute_group_id'] = attribute_group_id
        else:
            raise osv.except_osv(_('Attribute value creation error'),
                                 _('New attribute value creation allowed only from menu Product Attribute Groups or \
                                    from product form!'))
        return super(product_attribute_value, self).create(cr, uid, vals, context)

    _name = 'product.attribute.value'
    _columns = {
        'name': fields.char('Product attribute value name', size=64, required=True),
        'attribute_id': fields.many2one('product.attribute', 'Attribute', required=True, ondelete='restrict'),
        'attribute_group_id': fields.many2one('product.attribute.group', 'Attribute group', required=True,
                                              ondelete='restrict'),
    }
    _sql_constraints = [('name_attribute_group_unique', 'unique(name, attribute_id, attribute_group_id)',
                         'Attribute value must be unique!')]
product_attribute_value()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: