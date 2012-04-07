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
import decimal_precision as dp

class product_product(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'
    _columns = {
        'width': fields.integer('Width, mm', size=5, help="Width in mm"),
        'height': fields.integer('Height, mm', size=5, help="Height in mm"),
        'depth': fields.integer('Depth, mm', size=5, help="Depth in mm"),
        'volume_auto': fields.boolean('Auto calculate volume by sizes', help="If checked, volume computed by sizes"),
        'volume': fields.float('Volume, m3', digits=(2,3), help="The volume in m3."),
        'weight': fields.float('Gross weight, kg', digits_compute=dp.get_precision('Stock Weight'), help="The gross weight in Kg."),
        'weight_net': fields.float('Net weight, kg', digits_compute=dp.get_precision('Stock Weight'), help="The net weight in Kg."),
    }

    _defaults = {
        'volume_auto': lambda *a: True,
    }

    def onchange_sizes(self, cr, uid, ids, width, height, depth, volume_auto):
        v = {}
        if volume_auto:
            if width>0 and height>0 and depth>0:
                v['volume'] = width * height * depth / 1000000000.0
            else:
                v['volume'] = 0
            return {'value': v}
        else:
            return {}
product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: