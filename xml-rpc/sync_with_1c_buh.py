#!/usr/bin/env python
#coding: utf-8
#Скрипт выполняет синхронизацию OpenERP с 1С Бухгалтерией
#Автор - Денис Каратаев, 2012.

#Сразу выводим тим содержимого
print 'Content-Type: text/xml'
#Запрещаем кеширование
print 'Cache-Control: no-store, no-cache,  must-revalidate'
print 'Expires: 10 Aug 2010 10:00:00 +0400'
print

import cgi, cgitb
import smtplib
from email.mime.text import MIMEText
from xmlrpclib import ServerProxy, Fault
from xml.dom.minidom import Document
from lxml import etree

#Настройки базы
server = 'http://localhost:8069/xmlrpc/'
db = 'dbname'
uname = 'admin'
pwd = 'password'
context = {'lang': 'ru_RU'}

#Правильный ключ для соединения со скриптом извне
true_skey = '35c89a88133cfbd8fbd08e83a4454b1a'

#Данные для отправки уведомлений админу
mailto = 'mail@gmail.com'
smtp_server = 'smtp.gmail.com'
smtp_password = 'password'
#Логировать ли все обмены на почту
mail_log = True

def mail(message):
    msg = MIMEText(message)
    msg['Subject'] = 'Отчет об ошибках при синхронизации OpenERP с 1С Бухгалтерией'
    msg['From'] = mailto
    msg['To'] = mailto
    smtp = smtplib.SMTP_SSL()
    smtp.connect(smtp_server)
    smtp.login(mailto, smtp_password)
    smtp.sendmail(mailto, mailto, msg.as_string())
    smtp.quit()

#Основной код
try:
    #Для работы с CGI
    cgitb.enable()
    request = cgi.FieldStorage()

    #Проверяем, есть ли полномочия у запускающего скрипт
    skey = request.getvalue('skey')
    if skey != true_skey:
        raise Exception('Неправильный секретный ключ')

    #Подключаемся к базе и получаем uid пользователя
    sock = ServerProxy(server + 'object', allow_none=True)
    sock_common = ServerProxy(server + 'common')
    uid = sock_common.login(db, uname, pwd)

    #Проверяем, был ли послан файл
    if 'userfile' in request:
        userfile = request['userfile']
        if userfile.file:
            #Парсим XML файл
            doc = etree.parse(userfile.file)
            data = doc.xpath('/data')[0]

            #Получаем ответы о синхронизации продуктов
            info = ''.join((u'Журнал синхронизации с бухгалтерией ', data.get('title'), ':\r\n'))
            errors = u'При синхронизации OpenERP с 1С Бухгалтерией произошли следующие ошибки:\r\n'
            is_errors = False
            products = doc.xpath('/data/products/product')
            for product in products:
                if mail_log:
                    info = '\r\n'.join((info, u'Продукт %s: %s %s' % (product.get('id'), product.text, product.get('id_buh'))))
                if product.text != u'Создан элемент' and product.text != u'Обновлен элемент':
                    is_errors = True
                    errors = '\r\n'.join((errors, u'Продукт %s: %s %s' % (product.get('id'), product.text,
                                                                                            u'(Ошибка на стороне 1С)')))
            if mail_log:
                mail(info.encode('UTF-8'))
            #Если имеются ошибки, высылаем письмо админу
            if is_errors:
                mail(errors.encode('UTF-8'))
            doc = Document()
            xmlAnswer = doc.createElement('answer')
            xmlAnswerText = doc.createTextNode('ok')
            xmlAnswer.appendChild(xmlAnswerText)
            doc.appendChild(xmlAnswer)
            print doc.toprettyxml(indent='  ', encoding='UTF-8')
    else:
        #Файл нам не прислали, значит будем мы данные выводить для новой синхронизации
        doc = Document()
        xmlData = doc.createElement('data')
        doc.appendChild(xmlData)
        xmlProducts = doc.createElement('products')
        xmlData.appendChild(xmlProducts)

        product_ids = sock.execute(db, uid, pwd, 'product.product', 'search', [], 0, None, None, context)

        fields = ['id', 'name', 'taxes_id', 'uom_id']
        products = sock.execute(db, uid, pwd, 'product.product', 'read', product_ids, fields, context)
        for product in products:
            xmlProduct = doc.createElement('product')
            xmlProduct.setAttribute('id', str(product['id']))

            xmlProductName = doc.createElement('name')
            xmlProductNameText = doc.createTextNode(product['name'])
            xmlProductName.appendChild(xmlProductNameText)
            xmlProduct.appendChild(xmlProductName)

            vat = 0
            fields = ['amount', 'description']
            taxes = sock.execute(db, uid, pwd, 'account.tax', 'read', product['taxes_id'], fields, context)
            for tax in taxes:
                if tax['description'] == 'vat':
                    vat = int(tax['amount'] * 100)
                    break
            if not vat:
                raise Exception(' '.join(('Укажите ставку НДС у товара', product['name'].encode('UTF-8'))))
            xmlProductVat = doc.createElement('vat')
            xmlProductVatText = doc.createTextNode(str(vat))
            xmlProductVat.appendChild(xmlProductVatText)
            xmlProduct.appendChild(xmlProductVat)

            xmlProductUom = doc.createElement('uom')
            xmlProductUomText = doc.createTextNode(product['uom_id'][1])
            xmlProductUom.appendChild(xmlProductUomText)
            xmlProduct.appendChild(xmlProductUom)

            xmlProducts.appendChild(xmlProduct)
        print doc.toprettyxml(indent='  ', encoding='UTF-8')
except Exception,e:
    if isinstance(e, Fault):
        error_message = e.faultCode.encode('UTF-8')
    else:
        error_message = e.message
    mail(' '.join((error_message, '(OpenERP)')))
    print '<error>%s</error>' % error_message