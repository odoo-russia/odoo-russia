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
                raise osv.except_osv('Some attributes have references to this attribute group!', 'First remove these \
                                                                                references: ' + attribute_names_str)
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
        vals['name'] = vals['name'][0].upper() + vals['name'][1:]
        return super(product_attribute, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if 'name' in vals:
            vals['name'] = vals['name'][0].upper() + vals['name'][1:]
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
                raise osv.except_osv('Some attribute groups have references to this attribute!', 'First remove these \
                                                                            references: ' + attribute_group_names_str)
        return super(product_attribute_group, self).unlink(cr, uid, ids)

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
    }
    _order = 'type'
    _sql_constraints = [('attribute_name_unique','unique(name)','Attribute name must be unique!')]
product_attribute()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: