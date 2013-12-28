#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import urllib2
from StringIO import StringIO
from lxml import etree
from datetime import date, datetime
from tempfile import TemporaryFile
from dbfpy import dbf  # pip install http://downloads.sourceforge.net/project/dbfpy/dbfpy/2.2.5/dbfpy-2.2.5.tar.gz
from zipfile import ZipFile


CBRF_BIK_CATALOG_URL = 'http://www.cbr.ru/mcirabis/PluginInterface/GetBicCatalog.aspx'
CBRF_BIK_URL = 'http://www.cbr.ru/mcirabis/BIK/'
OUT_FILE = os.path.join(os.path.dirname(__file__), '../../data/res_bank_data.xml')


def generate_bank_file(out_file):

    catalog = etree.parse(StringIO(
        urllib2.urlopen(CBRF_BIK_CATALOG_URL).read()
    ))

    today = date.today()

    print 'Generation date : %s' % catalog.xpath('/BicDBList/@DataGeneration')[0]
    print 'Catalog hash    : %s' % catalog.xpath('/BicDBList/CatalogHash/@hash')[0]
    print 'Today           : %s' % today.strftime('%d.%m.%Y')

    metadata = [item.attrib
                for item in catalog.xpath('/BicDBList/item')
                if datetime.strptime(item.attrib['date'], '%d.%m.%Y').date() >= today
                ][0]

    bik_url = CBRF_BIK_URL + metadata['file']
    print 'Current bik url : %s' % bik_url
    bik_f = TemporaryFile()
    print 'Saving data to temporary file'
    bik_f.write(urllib2.urlopen(bik_url).read())
    bik_f.seek(0, os.SEEK_SET)

    z = ZipFile(bik_f)
    dbf_f = TemporaryFile()
    dbf_f.write(z.read('BNKSEEK.DBF'))
    z.close()

    db = dbf.Dbf(dbf_f)

    root = etree.Element('openerp')
    data = etree.SubElement(root, 'data')

    def _append_field(name, text):
        n = etree.SubElement(record, 'field', attrib={'name': name})
        n.text = text

    for rec in db:
        record = etree.SubElement(data, 'record', attrib={'model':'res.bank', 'id':'bank.%d' % i })
        _append_field('name',     rec['NAMEP'])
        _append_field('city',     rec['NNP'].decode('cp866'))
        _append_field('street',   rec['ADR'].decode('cp866'))
        _append_field('phone',    rec['TELEF'].decode('cp866'))
        _append_field('bic',      rec['NEWNUM'])
        _append_field('acc_corr', rec['KSNP'])
        _append_field('active',   'True')
        _append_field('last_updated', today.strftime('%Y%m%d'))
        etree.SubElement(record, 'field', attrib={'name': name, 'ref':'ru'})

    out_f = open(out_file, 'wb')
    out_f.write(etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8'))
    out_f.close()

    dbf_f.close()


if __name__ == '__main__':
    generate_bank_file(OUT_FILE)
