#########################################################################
# Copyright (C) 2009  Sharoon Thomas, Open Labs Business solutions      #
#                                                                       #
#This program is free software: you can redistribute it and/or modify   #
#it under the terms of the GNU General Public License as published by   #
#the Free Software Foundation, either version 3 of the License, or      #
#(at your option) any later version.                                    #
#                                                                       #
#This program is distributed in the hope that it will be useful,        #
#but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#GNU General Public License for more details.                           #
#                                                                       #
#You should have received a copy of the GNU General Public License      #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
#########################################################################
from osv import osv, fields

class product_images(osv.osv):
    def _get_filename(self, full_path):
        return full_path.replace('\\', '/').split('/')[-1]

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        vals['image_filename'] =  self._get_filename(vals['image_filename'])
        return super(product_images, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        vals['image_filename'] =  self._get_filename(vals['image_filename'])
        return super(product_images, self).write(cr, uid, ids, vals, context)

    def get_image(self, cr, uid, id):
        each = self.read(cr, uid, id, ['image'])
        return each['image']

    def _get_image(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        for each in ids:
            res[each] = self.get_image(cr, uid, each)
        return res

    _name = "product.images"
    _columns = {
        'name':fields.char('Image title', size=100),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of follow-up lines."),
        'type': fields.selection(
            [('image', 'Image'), ('scheme', 'Scheme'), ('flash3d', '3D flash animation')],
            'Image type', required=True),
        'image': fields.binary('Image', required=True),
        'image_filename': fields.char('Image filename', size=500),
        'preview': fields.function(_get_image, type="binary", method=True),
        'comments': fields.text('Comments'),
        'product_id': fields.many2one('product.product', 'Product', ondelete='cascade', required=True)
    }
    _order = 'sequence'
product_images()
