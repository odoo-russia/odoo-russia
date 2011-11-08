import xmlrpclib, sys
from xml.dom.minidom import Document

username = 'admin'
pwd = 'admin'
dbname = 'sungroupp'
server = 'http://dskarataev.ru:8069/xmlrpc/'

sock_common = xmlrpclib.ServerProxy(server + 'common')
uid = sock_common.login(dbname, username, pwd) or sys.exit('Bad username, password or database name!')

sock = xmlrpclib.ServerProxy(server + 'object')

product_ids = sock.execute(dbname, uid, pwd, 'product.product', 'search', [('active', '=', 1)])
#fields = []
fields = ['id', 'name', 'categ_id',
          'width', 'height', 'depth', 'volume', 'weight_net',
          'manufacturer_ids',
          'attribute_group', 'attribute_value_product_ids',
          'description_short', 'description',
          'image_ids']
products = sock.execute(dbname, uid, pwd, 'product.product', 'read', product_ids, fields, {'lang': 'ru_RU'})
print products
for product in products:
    if product['manufacturer_ids']:
        fields = ['id', 'name',
                  'product_country_id', 'product_brand_id',
                  'product_code', 'product_name']
        manufacturers = sock.execute(dbname, uid, pwd, 'product.manufacturer', 'read', product['manufacturer_ids'],
                                     fields, {'lang': 'ru_RU'})
        print manufacturers

    if product['attribute_value_product_ids']:
        fields = ['attribute_id', 'attribute_value_id']
        attributes = sock.execute(dbname, uid, pwd, 'product.attribute.value.product', 'read',
                                  product['attribute_value_product_ids'], fields, {'lang': 'ru_RU'})
        print attributes

    if product['image_ids']:
        fields = ['name', 'sequence', 'type', 'comments']
        images = sock.execute(dbname, uid, pwd, 'product.images', 'read', product['image_ids'], fields,
                            {'lang': 'ru_RU'})
        print images

#doc = Document()
#
#catalog = doc.createElement('catalog')
#doc.appendChild(catalog)
#
#print doc.toprettyxml(indent='  ')