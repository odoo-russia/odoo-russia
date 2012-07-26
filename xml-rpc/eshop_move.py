#coding: utf-8
#Скрипт выполняет перенос товаров, занесенных для интернет-магазина, из версии 6.0 в версию 6.1
#Автор - Денис Каратаев, 2012.

from xmlrpclib import ServerProxy, Fault

#Настройки первой базы
server1 = 'http://server1.ru:8069/xmlrpc/'
db1 = 'openerp'
uname1 = 'admin'
pwd1 = 'admin'

#Настройки второй базы
server2 = 'http://server2:8069/xmlrpc/'
db2 = 'openerp'
uname2 = 'admin'
pwd2 = 'admin'

#Рекурсивная функция добавления категорий в базу
def create_product_category(product_categories, old_parent_id=False, new_parent_id=False):
    #Определяем список категорий, которые нужно добавить в текущей итерации
    if old_parent_id:
        create_categories = [category for category in product_categories
                             if category['parent_id'] and category['parent_id'][0]==old_parent_id]
    else:
        create_categories = [category for category in product_categories if not category['parent_id']]

    for category in create_categories:
        #Если такие категории имеются, добавляем их
        if category['id']!=1:
            new_category = {
                'name': category['name'],
                'parent_id': new_parent_id,
                'vip': category['vip'],
            }
            new_category_id = sock2.execute(db2, uid2, pwd2, 'product.category', 'create', new_category,
                    {'lang': 'ru_RU'})
        else:
            new_category_id = 1

        map_category = {
            'id': category['id'],
            'new_id': new_category_id
        }
        global map_categories
        map_categories.append(map_category)

        if new_category_id==1:
            second_word = 'updated'
        else:
            second_word = 'added'
        global category_now
        print 'category %s: %d (%d from %d)' % (second_word, new_category_id, category_now, categories_count)
        category_now += 1

        #Запускаем эту же функцию для детей
        create_product_category(product_categories, category['id'], new_category_id)

try:
    #Подключаемся к первой базе и получаем uid пользователя
    sock1 = ServerProxy(server1 + 'object')
    sock_common1 = ServerProxy(server1 + 'common')
    uid1 = sock_common1.login(db1, uname1, pwd1) 

    #Подключаемся ко второй базе и получаем uid пользователя
    sock2 = ServerProxy(server2 + 'object')
    sock_common2 = ServerProxy(server2 + 'common')
    uid2 = sock_common2.login(db2, uname2, pwd2)

    #Сначала очистим уже занесенные товары
    product_ids2 = sock2.execute(db2, uid2, pwd2, 'product.product', 'search', [('eshop_sync', '=', True)])
    sock2.execute(db2, uid2, pwd2, 'product.product', 'unlink', product_ids2)

    #Переносим категории продукции

    #Сначала очистим категории во второй базе
    product_category_ids2 = sock2.execute(db2, uid2, pwd2, 'product.category', 'search', [])

    #Убираем из списка на удаление категорию с id = 1 т.к. она неудаляема
    product_category_ids2.remove(1)
    sock2.execute(db2, uid2, pwd2, 'product.category', 'unlink', product_category_ids2)

    #Теперь получаем категории из первой базы
    product_category_ids1 = sock1.execute(db1, uid1, pwd1, 'product.category', 'search', [])


    fields = ['id', 'name', 'parent_id', 'vip']
    product_categories1 = sock1.execute(db1, uid1, pwd1, 'product.category', 'read', product_category_ids1, fields,
                                        {'lang': 'ru_RU'})

    print '\nMoving categories...'
    map_categories = []
    categories_count = len(product_categories1)
    category_now = 1
    create_product_category(product_categories1)

    #Удаляем значения характеристик
    product_attribute_value_ids2 = sock2.execute(db2, uid2, pwd2, 'product.attribute.value', 'search', [])
    sock2.execute(db2, uid2, pwd2, 'product.attribute.value', 'unlink', product_attribute_value_ids2)

    #Удаляем связи между группами характеристик и характеристиками
    product_attribute_group_ids2 = sock2.execute(db2, uid2, pwd2, 'product.attribute.group', 'search', [])
    values = {
        'attribute_ids': [(6, 0, [])]
    }
    sock2.execute(db2, uid2, pwd2, 'product.attribute.group', 'write', product_attribute_group_ids2, values)

    #Переносим группы характеристик

    #Сначала очистим группы характеристик во второй базе
    sock2.execute(db2, uid2, pwd2, 'product.attribute.group', 'unlink', product_attribute_group_ids2)


    #Теперь получаем группы характеристик из первой базы
    product_attribute_group_ids1 = sock1.execute(db1, uid1, pwd1, 'product.attribute.group', 'search', [])


    fields = ['id', 'name', 'attribute_ids']
    product_attribute_groups1 = sock1.execute(db1, uid1, pwd1, 'product.attribute.group', 'read',
                                product_attribute_group_ids1, fields, {'lang': 'ru_RU'})
    attribute_groups_count = len(product_attribute_groups1)
    attribute_group_now = 1

    print '\nMoving attribute groups...'
    for attribute_group in product_attribute_groups1:
        new_attribute_group = {
            'name': attribute_group['name'],
        }
        new_attribute_group_id = sock2.execute(db2, uid2, pwd2, 'product.attribute.group',
                                               'create', new_attribute_group)

        attribute_group['new_id'] = new_attribute_group_id
        print 'attribute group added: %d (%d from %d)' % (new_attribute_group_id, attribute_group_now,
                                                          attribute_groups_count)
        attribute_group_now += 1

    #Переносим характеристики

    #Сначала очистим характеристики во второй базе
    product_attribute_ids2 = sock2.execute(db2, uid2, pwd2, 'product.attribute', 'search', [])
    sock2.execute(db2, uid2, pwd2, 'product.attribute', 'unlink', product_attribute_ids2)

    #Теперь получаем характеристики из первой базы
    product_attribute_ids1 = sock1.execute(db1, uid1, pwd1, 'product.attribute', 'search', [])


    fields = ['id', 'name', 'type']
    product_attributes1 = sock1.execute(db1, uid1, pwd1, 'product.attribute', 'read', product_attribute_ids1, fields,
            {'lang': 'ru_RU'})
    attributes_count = len(product_attributes1)
    attribute_now = 1

    print '\nMoving attributes...'
    for attribute in product_attributes1:
        new_attribute = {
            'name': attribute['name'],
            'type': attribute['type'],
            }
        new_attribute_id = sock2.execute(db2, uid2, pwd2, 'product.attribute', 'create', new_attribute)

        attribute['new_id'] = new_attribute_id
        print 'attribute added: %d (%d from %d)' % (new_attribute_id, attribute_now, attributes_count)
        attribute_now += 1

    #Связываем группы характеристик с характеристиками
    print '\nLinking attribute groups with attributes...'
    attribute_group_now = 1
    for product_attribute_group1 in product_attribute_groups1:
        if product_attribute_group1['attribute_ids']:
            new_attribute_ids = []
            for old_attribute_id in product_attribute_group1['attribute_ids']:
                new_attribute_id = [attribute1['new_id'] for attribute1 in product_attributes1
                                    if attribute1['id'] == old_attribute_id]
                new_attribute_ids.append(new_attribute_id[0])
            values = {
                'attribute_ids': [(6, 0, new_attribute_ids)]
            }
            sock2.execute(db2, uid2, pwd2, 'product.attribute.group', 'write', [product_attribute_group1['new_id']],
                                                                                                            values)
            print 'attribute group %d linked with attributes: %s (%d from %d)' % (product_attribute_group1['new_id'],
                                                                                  ', '.join(map(str, new_attribute_ids)),
                                                                                  attribute_group_now,
                                                                                  attribute_groups_count)
            attribute_group_now += 1

    #Переносим значения характеристик
    product_attribute_value_ids1 = sock1.execute(db1, uid1, pwd1, 'product.attribute.value', 'search', [])

    fields = ['id', 'name', 'attribute_id', 'attribute_group_id']
    product_attribute_values1 = sock1.execute(db1, uid1, pwd1, 'product.attribute.value', 'read',
                                              product_attribute_value_ids1, fields, {'lang': 'ru_RU'})
    attribute_values_count = len(product_attribute_values1)
    attribute_value_now = 1

    print '\nMoving attribute values...'
    for attribute_value in product_attribute_values1:
        #поиск attribute_id и attribute_group_id в новой базе
        new_attribute_id = [attribute1['new_id'] for attribute1 in product_attributes1
                            if attribute1['id'] == attribute_value['attribute_id'][0]][0]
        new_attribute_group_id = [attribute_group1['new_id'] for attribute_group1 in product_attribute_groups1
                            if attribute_group1['id'] == attribute_value['attribute_group_id'][0]][0]

        new_attribute_value = {
            'name': attribute_value['name'],
            'attribute_id': new_attribute_id,
            'attribute_group_id': new_attribute_group_id
        }
        new_attribute_value_id = sock2.execute(db2, uid2, pwd2, 'product.attribute.value',
                                               'create', new_attribute_value)

        attribute_value['new_id'] = new_attribute_value_id
        print 'attribute value added: %d (%d from %d)' % (new_attribute_value_id, attribute_value_now,
                                                          attribute_values_count)
        attribute_value_now += 1

    #Переносим базовые поля товаров
    product_ids1 = sock1.execute(db1, uid1, pwd1, 'product.product', 'search', [])

    fields = ['id', 'name', 'categ_id',
              'width', 'height', 'depth', 'volume_auto', 'volume', 'weight_net',
              'hit', 'new', 'description', 'description_short', 'attribute_group']
    products1 = sock1.execute(db1, uid1, pwd1, 'product.product', 'read', product_ids1, fields, {'lang': 'ru_RU'})
    products_count = len(products1)
    product_now = 1

    print '\nMoving products...'
    for product in products1:
        #поиск categ_id и attribute_group_id в новой базе
        new_categ_id = [category['new_id'] for category in map_categories
                        if category['id'] == product['categ_id'][0]][0]
        new_attribute_group_id = [attribute_group1['new_id'] for attribute_group1 in product_attribute_groups1
                                  if attribute_group1['id'] == product['attribute_group'][0]][0]
        new_product = {
            'eshop_sync': True,
            'name_eshop': product['name'],
            'categ_id': new_categ_id,
            'width': product['width'],
            'height': product['height'],
            'depth': product['depth'],
            'volume_auto': product['volume_auto'],
            'volume': product['volume'],
            'weight_net': product['weight_net'],
            'hit': product['hit'],
            'new': product['new'],
            'description': product['description'],
            'description_short': product['description_short'],
            'attribute_group': new_attribute_group_id
        }
        new_product_id = sock2.execute(db2, uid2, pwd2, 'product.product', 'create', new_product)

        product['new_id'] = new_product_id
        print 'product added: %d (%d from %d)' % (new_product_id, product_now, products_count)
        product_now += 1

    #Связываем товары с характеристиками и их значениями
    product_attribute_value_product_ids1 = sock1.execute(db1, uid1, pwd1, 'product.attribute.value.product',
                                                         'search', [])

    fields = ['id', 'attribute_id', 'attribute_value_id', 'checkbx_value', 'product_id']
    product_attribute_value_products1 = sock1.execute(db1, uid1, pwd1, 'product.attribute.value.product',
                                                'read', product_attribute_value_product_ids1, fields, {'lang': 'ru_RU'})
    attribute_value_products_count = len(product_attribute_value_products1)
    attribute_value_product_now = 1

    print '\nLinking products with attributes and values...'
    for attribute_value_product in product_attribute_value_products1:
        #поиск актуальных ссылок на attribute_id, attribute_value_id и product_id
        new_product_id = [product1['new_id'] for product1 in products1
                          if product1['id'] == attribute_value_product['product_id'][0]][0]
        new_attribute_id = [attribute1['new_id'] for attribute1 in product_attributes1
                            if attribute1['id'] == attribute_value_product['attribute_id'][0]][0]
        #узнаем тип характеристики, чтобы понять, нужна ли нам ссылка на значение, или значение хранится в поле
        #checkbx_value
        if [attribute1['type'] for attribute1 in product_attributes1
            if attribute1['new_id'] == new_attribute_id][0] == 'string':
            new_attribute_value_id = [attribute_value1['new_id'] for attribute_value1 in product_attribute_values1
                                      if attribute_value1['id'] == attribute_value_product['attribute_value_id'][0]][0]
        else:
            new_attribute_value_id = False

        new_attribute_value_product = {
            'attribute_id': new_attribute_id,
            'attribute_value_id': new_attribute_value_id,
            'product_id': new_product_id,
            'checkbx_value': attribute_value_product['checkbx_value']
        }
        new_attribute_value_product_id = sock2.execute(db2, uid2, pwd2, 'product.attribute.value.product',
                                                       'create', new_attribute_value_product)

        attribute_value_product['new_id'] = new_attribute_value_product_id
        print 'product %d linked with attribute %d and value %d (%d from %d)' % (new_product_id, new_attribute_id,
                                                                                 new_attribute_value_id,
                                                                                 attribute_value_product_now,
                                                                                 attribute_value_products_count)
        attribute_value_product_now += 1

    #Переносим изображения
    product_images_ids1 = sock1.execute(db1, uid1, pwd1, 'product.images', 'search', [])
    fields = ['id', 'name', 'sequence', 'type', 'image', 'image_filename', 'comments', 'product_id']
    product_images_count = len(product_images_ids1)
    product_image_now = 1

    print '\nMoving images and linking with products...'
    #Получаем из базы не сразу все картинки, а по одной, чтобы не перегрузить сервер, т.к. скорее всего он зависнет от
    #большого количества крупных и тяжелых картинок
    for product_image_id in product_images_ids1:
        product_image = sock1.execute(db1, uid1, pwd1, 'product.images', 'read', product_image_id, fields,
                                      {'lang': 'ru_RU'})
        #ищем актуальный product_id
        new_product_id = [product1['new_id'] for product1 in products1
                          if product1['id'] == product_image['product_id'][0]][0]
        new_product_image = {
            'name': product_image['name'],
            'sequence': product_image['sequence'],
            'type': product_image['type'],
            'image': product_image['image'],
            'image_filename': product_image['image_filename'],
            'comments': product_image['comments'],
            'product_id': new_product_id
        }
        new_product_image_id = sock2.execute(db2, uid2, pwd2, 'product.images', 'create', new_product_image)

        print 'product image added: %d, linked with product %d (%d from %d)' % (new_product_image_id, new_product_id,
                                                                                product_image_now, product_images_count)
        product_image_now += 1

    #Очищаем бренды
    brand_ids2 = sock2.execute(db2, uid2, pwd2, 'product.brand', 'search', [])
    sock2.execute(db2, uid2, pwd2, 'product.brand', 'unlink', brand_ids2)

    #Очищаем партнеров
    partner_ids2 = sock2.execute(db2, uid2, pwd2, 'res.partner', 'search', [('id', '!=', 1)])
    sock2.execute(db2, uid2, pwd2, 'res.partner', 'unlink', partner_ids2)

    #Переносим партнеров
    partner_ids1 = sock1.execute(db1, uid1, pwd1, 'res.partner', 'search', [])
    fields = ['id', 'name']
    partners1 = sock1.execute(db1, uid1, pwd1, 'res.partner', 'read', partner_ids1, fields, {'lang': 'ru_RU'})
    partners_count = len(partners1)
    partner_now = 1

    print '\nMoving partners...'
    for partner in partners1:
        new_partner = {
            'name': partner['name'],
        }
        new_partner_id = sock2.execute(db2, uid2, pwd2, 'res.partner', 'create', new_partner)
        partner['new_id'] = new_partner_id

        print 'partner added: %d (%d from %d)' % (new_partner_id, partner_now, partners_count)
        partner_now += 1

    #Переносим бренды
    product_brand_ids1 = sock1.execute(db1, uid1, pwd1, 'product.brand', 'search', [])
    fields = ['id', 'name', 'description', 'logo', 'logo_filename', 'partner_id']
    product_brands1 = sock1.execute(db1, uid1, pwd1, 'product.brand', 'read', product_brand_ids1, fields,
                                    {'lang': 'ru_RU'})
    product_brands_count = len(product_brands1)
    product_brand_now = 1

    print '\nMoving brands and linking with partners...'
    for brand in product_brands1:
        #определяем актуальный partner_id
        new_partner_id = [partner1['new_id'] for partner1 in partners1 if partner1['id'] == brand['partner_id'][0]][0]

        new_brand = {
            'name': brand['name'],
            'description': brand['description'],
            'logo': brand['logo'],
            'logo_filename': brand['logo_filename'],
            'partner_id': new_partner_id
        }
        new_brand_id = sock2.execute(db2, uid2, pwd2, 'product.brand', 'create', new_brand)

        brand['new_id'] = new_brand_id
        print 'brand %d added and linked with partner %d (%d from %d)' % (new_brand_id, new_partner_id,
                                                                          product_brand_now, product_brands_count)
        product_brand_now += 1

    #Переносим производителей
    product_manufacturer_ids1 = sock1.execute(db1, uid1, pwd1, 'product.manufacturer', 'search', [])
    fields = ['id', 'name', 'product_name', 'product_code', 'product_country_id', 'product_brand_id', 'product_id']
    product_manufacturers1 = sock1.execute(db1, uid1, pwd1, 'product.manufacturer', 'read',
                                           product_manufacturer_ids1, fields, {'lang': 'ru_RU'})
    product_manufacturers_count = len(product_manufacturers1)
    product_manufacturer_now = 1

    print '\nMoving manufacturers...'
    for manufacturer in product_manufacturers1:
        #определяем актуальные partner_id product_brand_id и product_id
        new_partner_id = [partner1['new_id'] for partner1 in partners1
                          if partner1['id'] == manufacturer['name'][0]][0]
        #бренд не у всех может быть проставлен
        if manufacturer['product_brand_id']:
            new_brand_id = [brand1['new_id'] for brand1 in product_brands1
                            if brand1['id'] == manufacturer['product_brand_id'][0]][0]
        else:
            new_brand_id = False
        new_product_id = [product1['new_id'] for product1 in products1
                           if product1['id'] == manufacturer['product_id'][0]][0]
        #страна не у всех может быть проставлена
        if manufacturer['product_country_id']:
            fields = ['code']
            country1 = sock1.execute(db1, uid1, pwd1, 'res.country', 'read', manufacturer['product_country_id'][0],
                                     fields)
            country_ids2 = sock2.execute(db2, uid2, pwd2, 'res.country', 'search', [('code', '=', country1['code'])])
            if country_ids2:
                new_country_id = country_ids2[0]
            else:
                message = 'Bad country code: %s' % country1['code']
                exit(message)
        else:
            new_country_id = False

        new_manufacturer = {
            'name': new_partner_id,
            'product_name': manufacturer['product_name'],
            'product_code': manufacturer['product_code'],
            'product_country_id': new_country_id,
            'product_brand_id': new_brand_id,
            'product_id': new_product_id
        }
        new_manufacturer_id = sock2.execute(db2, uid2, pwd2, 'product.manufacturer', 'create', new_manufacturer)

        manufacturer['new_id'] = new_manufacturer_id
        print 'manufacturer %d added and linked with brand %d and product %d (%d from %d)' % (new_manufacturer_id,
            new_brand_id, new_product_id, product_manufacturer_now, product_manufacturers_count)
        product_manufacturer_now += 1
except Fault,e:
    print e