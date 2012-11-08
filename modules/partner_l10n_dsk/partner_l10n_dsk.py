#coding: utf-8
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
from tools.translate import _
from datetime import date
from csv import reader
import urllib2

csvBnkseekPath = 'http://openerp-russia.ru/bank/bnkseek.txt'
csvBnkdelPath = 'http://openerp-russia.ru/bank/bnkdel.txt'
csvDelimiter = '\t'
csvEncoding = 'windows-1251'

our_country = u'Российская Федерация'

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
        'contract_num': fields.char('Contract number', size=64),
        'contract_date': fields.date('Contract date'),
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
        'last_updated': fields.char('Last updated', size=8)
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

class wizard_update_banks(osv.osv_memory):
    def update_banks(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        bank = self.pool.get('res.bank')
        try:
            bnkseek = urllib2.urlopen(context.get('location_bnkseek'))
        except urllib2.HTTPError, err:
            raise osv.except_osv(_('Bad URL for bnkseek.txt!'), _('Fix the URL and try again.'))
        csv = csv_reader(bnkseek, csvEncoding, delimiter=csvDelimiter)

        today_str = date.today().strftime('%Y%m%d')

        #Ищем нашу страну
        country_ids = self.pool.get('res.country').search(cr, uid, [('name', '=', our_country)], context=context)
        if not country_ids or len(country_ids) != 1:
            raise osv.except_osv(_('Country Error: %s') % our_country)
        our_country_id = country_ids[0]

        for row in csv:
            name = row[3].strip()
            city = row[1].strip()
            bic = row[5].strip()
            acc_corr = row[6].strip()

            context['active_test'] = False
            ids = bank.search(cr, uid, [('bic', '=', bic)], context=context)
            if ids:
                values = {
                    'name': name,
                    'city': city,
                    'country': our_country_id,
                    'acc_corr': acc_corr,
                    'active': True,
                    'last_updated': today_str,
                }
                bank.write(cr, uid, ids, values, context=context)
            else:
                values = {
                    'name': name,
                    'city': city,
                    'country': our_country_id,
                    'bic': bic,
                    'acc_corr': acc_corr,
                    'active': True,
                    'last_updated': today_str,
                }
                bank.create(cr, uid, values, context=context)
        try:
            bnkdel = urllib2.urlopen(context.get('location_bnkdel'))
        except urllib2.HTTPError, err:
            raise osv.except_osv(_('Bad URL for bnkdel.txt!'), _('Fix the URL and try again.'))
        csv = csv_reader(bnkdel, csvEncoding, delimiter=csvDelimiter)
        for row in csv:
            bic = row[6].strip()
            deleted = row[1].strip()

            ids = bank.search(cr, uid, [('bic', '=', bic), ('last_updated', '<=', deleted)], context=context)
            if ids:
                values = {
                    'active': False,
                }
                bank.write(cr, uid, ids, values, context=context)
        return {
            'view_type': 'form,tree',
            'view_mode': 'tree',
            'res_model': 'res.bank',
            'type': 'ir.actions.act_window',
        }

    _name = 'wizard.update.banks'
    _columns = {
        'location_bnkseek': fields.char('Location of bnkseek.txt', size=500),
        'location_bnkdel': fields.char('Location of bnkdel.txt', size=500),
    }
    _defaults = {
        'location_bnkseek': lambda *a: csvBnkseekPath,
        'location_bnkdel': lambda *a: csvBnkdelPath,
    }
wizard_update_banks()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: