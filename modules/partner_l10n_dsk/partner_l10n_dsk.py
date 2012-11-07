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
from csv import reader
import urllib2

csvBnkseekPath = 'http://openerp-russia.ru/bank/bnkseek.txt'
csvBnkdelPath = 'http://openerp-russia.ru/bank/bnkdel.txt'
csvDelimiter = '\t'
csvEncoding = 'windows-1251'

def csv_reader(iterable, encoding='utf-8', **kwargs):
    csv_reader = reader(iterable, **kwargs)
    for row in csv_reader:
        # decode UTF-8 to Unicode, cell by cell:
        yield [unicode(cell, encoding) for cell in row]

class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _columns = {
        'name_official': fields.char('Official name', size=200),
        'inn': fields.char('INN', size=12),
        'kpp': fields.char('KPP', size=9),
        'okpo': fields.char('OKPO', size=14),
    }
res_partner()

#Fixing the problem with country name. Showing it in russian translation.
class res_partner_address(osv.osv):
    _name = 'res.partner.address'
    _inherit = 'res.partner.address'

    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if not len(ids):
            return []
        res = []
        for r in self.read(cr, user, ids, ['name','zip','country_id', 'city','partner_id', 'street'], context):
            if context.get('contact_display', 'contact')=='partner' and r['partner_id']:
                res.append((r['id'], r['partner_id'][1]))
            else:
                # make a comma-separated list with the following non-empty elements
                elems = [r['name'], r['country_id'] and r['country_id'][1], r['city'], r['street']]
                addr = ', '.join(filter(bool, elems))
                if (context.get('contact_display', 'contact')=='partner_address') and r['partner_id']:
                    res.append((r['id'], "%s: %s" % (r['partner_id'][1], addr or '/')))
                else:
                    res.append((r['id'], addr or '/'))
        return res
res_partner_address()

class Bank(osv.osv):
    _name = 'res.bank'
    _inherit = 'res.bank'
    _columns = {
        'acc_corr': fields.char('Corr. account', size=64),
    }
Bank()

class res_partner_bank(osv.osv):
    _name = 'res.partner.bank'
    _inherit = 'res.partner.bank'
    _columns = {
        'bank_acc_corr': fields.char('Corr. account', size=64),
    }

    def onchange_bank_id(self, cr, uid, ids, bank_id, context=None):
        result = {}
        if bank_id:
            bank = self.pool.get('res.bank').browse(cr, uid, bank_id, context=context)
            result['bank_name'] = bank.name
            result['bank_bic'] = bank.bic
            result['bank_acc_corr'] = bank.acc_corr
        return {'value': result}
res_partner_bank()

class res_bank_tmp(osv.osv):
    _name = 'res.bank.tmp'
    _description= 'Changes in Banks'
    _columns = {
        'name': fields.char('Name', size=500, required=True),
        'city': fields.char('City', size=100, required=True),
        'bik': fields.char('BIK', size=64, required=True),
        'acc_corr': fields.char('Corr. account', size=64),
        'bank_id': fields.many2one('wizard.update.banks'),
    }
res_bank_tmp()

class wizard_update_banks(osv.osv_memory):
    def load_banks(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        banks_tmp = self.pool.get('res.bank.tmp')
        ids = banks_tmp.search(cr, uid, [], context=context)
        banks_tmp.unlink(cr, uid, ids, context=context)
        bnkseek = urllib2.urlopen(csvBnkseekPath)
        csv = csv_reader(bnkseek, csvEncoding, delimiter=csvDelimiter)
        for row in csv:
            values = {
                'name': row[3].strip(),
                'city': row[1].strip(),
                'bik':  row[5].strip(),
                'acc_corr': row[6].strip(),
                'bank_id': 1,
            }
            self.pool.get('res.bank.tmp').create(cr, uid, values, context=context)
        return {}

    def save_banks(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

    _name = 'wizard.update.banks'
    _columns = {
        'banks': fields.one2many('res.bank.tmp', 'bank_id', 'Changes in Banks', required=True),
    }
wizard_update_banks()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: