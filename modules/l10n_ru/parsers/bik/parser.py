#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Генерация справочника банков


import os
import urllib2
from StringIO import StringIO
from lxml import etree
from datetime import date, datetime
from tempfile import TemporaryFile
from dbfpy import dbf  # pip install http://downloads.sourceforge.net/project/dbfpy/dbfpy/2.2.5/dbfpy-2.2.5.tar.gz
from zipfile import ZipFile


CBRF_BIC_CATALOG_URL = 'http://www.cbr.ru/mcirabis/PluginInterface/GetBicCatalog.aspx'
CBRF_BASE_BIC_URL = 'http://www.cbr.ru/mcirabis/BIK/'
OUT_FILE = os.path.join(os.path.dirname(__file__), '../../data/res_bank_data.xml')


def get_bic_list(catalog_url=CBRF_BIC_CATALOG_URL, base_bic_url=CBRF_BASE_BIC_URL):
    catalog = etree.parse(StringIO(
        urllib2.urlopen(catalog_url).read()
    ))

    today = date.today()

    print 'Catalog hash    : %s' % catalog.xpath('/BicDBList/CatalogHash/@hash')[0]
    print 'Generation date : %s' % catalog.xpath('/BicDBList/@DataGeneration')[0]
    print 'Today           : %s' % today.strftime('%d.%m.%Y')

    metadata = [item.attrib
                for item in catalog.xpath('/BicDBList/item')
                if datetime.strptime(item.attrib['date'], '%d.%m.%Y').date() >= today
                ][0]

    bic_url = base_bic_url + metadata['file']
    print 'Current bik url : %s' % bic_url

    bic_list = []

    with TemporaryFile() as f:
        print 'Saving data to temporary file'
        f.write(urllib2.urlopen(bic_url).read())
        f.seek(0, os.SEEK_SET)
        with TemporaryFile() as df:
            z = ZipFile(f)
            df.write(z.read('BNKSEEK.DBF'))
            db = dbf.Dbf(df)

            for rec in db:
                bic_list.append({
                    'name': rec['NAMEP'].decode('cp866'),
                    'city': rec['NNP'].decode('cp866'),
                    'street': rec['ADR'].decode('cp866'),
                    'phone': rec['TELEF'].decode('cp866'),
                    'bic': rec['NEWNUM'],
                    'acc_corr': rec['KSNP'],
                    'active': 'True',
                    'last_updated': today.strftime('%Y%m%d'),
                })

    return bic_list


def generate_bank_file(out_file):
    bic_list = get_bic_list()

    def _append_field(name, text):
        if not name:
            name = chr(32)
        n = etree.SubElement(record, 'field', attrib={'name': name})
        n.text = text

    root = etree.Element('openerp')
    data = etree.SubElement(root, 'data', attrib={'noupdate': '0'})

    for bic in bic_list:
        record = etree.SubElement(data, 'record',
                                  attrib={'model': 'res.bank',
                                          'id': 'bank_%s' % bic['bic']})
        for k, v in bic.items():
            _append_field(k, v)
        etree.SubElement(record, 'field', attrib={'model': 'res.country',
                                                  'name': 'country',
                                                  'ref': 'base.ru'})

    with open(out_file, 'wb') as f:
        f.write(etree.tostring(root,
                               pretty_print=True,
                               xml_declaration=True,
                               encoding='utf-8'))


if __name__ == '__main__':
    generate_bank_file(OUT_FILE)
