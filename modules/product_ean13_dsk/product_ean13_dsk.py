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

class product_product(osv.osv):
    def _check_ean_key(self, cr, uid, ids, context=None):
        for product in self.browse(cr, uid, ids, context=context):
            print 'yes'
            eancode = product.ean13
            if not eancode:
                return True
            if len(eancode) <> 13:
                return False
            try:
                int(eancode)
            except:
                return False
            return True

    _name = 'product.product'
    _inherit = 'product.product'
    _constraints = [(_check_ean_key, 'Error: Invalid ean code', ['ean13'])]
    _sql_constraints = [('ean_code_unique','unique(ean13)','EAN code must be unique!')]
product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: