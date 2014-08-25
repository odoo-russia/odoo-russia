# -*- coding: utf-8 -*-

import os
import urllib2
from StringIO import StringIO
from datetime import date, datetime
from tempfile import TemporaryFile
from dbfpy import dbf  # pip install http://downloads.sourceforge.net/project/dbfpy/dbfpy/2.2.5/dbfpy-2.2.5.tar.gz
from zipfile import ZipFile
from lxml import etree
import logging


def get_bic_list(catalog_url=None, base_bic_url=None):
    """
    Функция загрузки БИК с сайта ЦБ РФ
    :param catalog_url: URL файла метаданных справочника БИК
    :param base_bic_url: базовый URL для текущих архивов БИК
    :return: словарь с записями БИК
    """
    if not catalog_url:
        catalog_url = 'http://www.cbr.ru/mcirabis/PluginInterface/GetBicCatalog.aspx'
    if not base_bic_url:
        base_bic_url = 'http://www.cbr.ru/mcirabis/BIK/'

    catalog = etree.parse(StringIO(
        urllib2.urlopen(catalog_url).read()
    ))

    today = date.today()

    logging.debug('Catalog hash    : %s' % catalog.xpath('/BicDBList/CatalogHash/@hash')[0])
    logging.debug('Generation date : %s' % catalog.xpath('/BicDBList/@DataGeneration')[0])
    logging.debug('Today           : %s' % today.strftime('%d.%m.%Y'))

    metadata = [item.attrib
                for item in catalog.xpath('/BicDBList/item')
                if datetime.strptime(item.attrib['date'], '%d.%m.%Y').date() >= today
                ][0]

    bic_url = base_bic_url + metadata['file']
    logging.debug('Current bik url : %s' % bic_url)

    bank_list = {}

    with TemporaryFile() as f:
        logging.debug('Saving data to temporary file')
        f.write(urllib2.urlopen(bic_url).read())
        f.seek(0, os.SEEK_SET)
        z = ZipFile(f)
        with TemporaryFile() as df:
            df.write(z.read('BNKSEEK.DBF'))
            db = dbf.Dbf(df)
            for rec in db:
                bank_list[rec['NEWNUM']] = {
                    'name': rec['NAMEP'].decode('cp866'),
                    'city': rec['NNP'].decode('cp866'),
                    'street': rec['ADR'].decode('cp866'),
                    'phone': rec['TELEF'].decode('cp866'),
                    'bic': rec['NEWNUM'],
                    'acc_corr': rec['KSNP'],
                    'zip': rec['IND'],
                    'active': 'True',
                    'last_updated': today.strftime('%Y%m%d'),
                }

        with TemporaryFile() as df:
            df.write(z.read('BNKDEL.DBF'))
            db = dbf.Dbf(df)
            for rec in db:
                if rec['NEWNUM'] in bank_list.keys():
                    # TODO: проверка даты отзыва лицензии
                    bank_list[rec['NEWNUM']]['active'] = 'False'

    return bank_list
