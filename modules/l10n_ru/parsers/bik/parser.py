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


def generate_bank_file():

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
    out_f = open(OUT_FILE, 'w')
    out_f.write('<?xml version="1.0" encoding="utf-8"?>\n'
                '<openerp>\n'
                '\t<data noupdate="0">\n')
    for rec in db:
        out_f.write("""\t\t<record model="res.country" id="bank.%s">
\t\t\t<field name="name">%s</field>
\t\t\t<field name="city">%s</field>
\t\t\t<field name="street">%s</field>
\t\t\t<field name="phone">%s</field>
\t\t\t<field name="country" ref="ru"/>
\t\t\t<field name="bic">%s</field>
\t\t\t<field name="acc_corr">%s</field>
\t\t\t<field name="active">True</field>
\t\t\t<field name="last_updated">%s</field>
\t\t</record>\n""" % (rec['KSNP'],
                      rec['NAMEP'].decode('cp866').encode('utf-8'),
                      rec['NNP'].decode('cp866').encode('utf-8'),
                      rec['ADR'].decode('cp866').encode('utf-8'),
                      rec['TELEF'].decode('cp866').encode('utf-8'),
                      rec['NEWNUM'],
                      rec['KSNP'],
                      today.strftime('%Y%m%d')))
    out_f.write('\t</data>\n</openerp>')
    out_f.close()
    dbf_f.close()


if __name__ == '__main__':
    generate_bank_file()
