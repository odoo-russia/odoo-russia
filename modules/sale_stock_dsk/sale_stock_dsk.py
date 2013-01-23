# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from osv import fields, osv, orm

class product_product(osv.osv):
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        if context is None:
            context = {}
        partner_id = context.get('partner_id')
        quantity = context.get('quantity')
        if not partner_id or not quantity:
            return super(product_product, self).name_get(cr, uid, ids, context=context)
        result = self.browse(cr, uid, ids, context=context)
        res = []
        for rs in result:
            res.append((rs.id, '%s (%s on hand, %s forecasted)' % (rs.name, rs.qty_available, rs.virtual_available)))
        return res

    _name = 'product.product'
    _inherit = 'product.product'
product_product()