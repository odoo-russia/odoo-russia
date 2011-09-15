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
import base64, urllib

class product_images(osv.osv):
    "Products Image gallery"
    _name = "product.images"
    _description = __doc__
    _table = "product_images"

    def _check_references(self, cr, uid, ids):
        for image in self.browse(cr, uid, ids):
            if image == image.product_id.image and image.type == 'flash3d' \
            or image == image.product_id.animation and image.type != 'flash3d':
                return False
        return True
            
    
    def get_image(self, cr, uid, id):
        each = self.read(cr, uid, id, ['image'])
        return each['image']
    
    def _get_image(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        for each in ids:
            res[each] = self.get_image(cr, uid, each)
        return res
    
    _columns = {
        'name':fields.char('Image title', size=100, required=True),
        'type': fields.selection(
            [('image', 'Image'), ('image3d', '3D Image'), ('scheme', 'Scheme'), ('flash3d', '3D flash animation')],
            'Image type', required=True),
        'image':fields.binary('Image', filters='*.png,*.jpg,*.swf', required=True),
        'preview':fields.function(_get_image, type="binary", method=True),
        'comments':fields.text('Comments'),
        'product_id':fields.many2one('product.product', 'Product', required=True)
    }

    _constraints = [
        (_check_references, 'You can\'t change image type when this image is product default image!', ['type'])
    ]
product_images()
