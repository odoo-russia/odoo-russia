#coding: utf-8

from openerp.osv import fields, osv
from utils import get_bic_list


class res_partner(osv.osv):
    def _format_address(self, cr, uid, ids, field, arg, context=None):
        res = {}

        for partner in self.browse(cr, uid, ids, context):
            address = [partner.zip, partner.country_id.name, partner.state_id.name, partner.city, partner.street]
            address = filter(bool, address)
            address = filter(None, address)
            res[partner.id] = ', '.join(address) if address else ""
        return res

    def _get_official_name_multi(self, cr, uid, ids, field, arg, context=None):
        res = {}
        for partner in self.browse(cr, uid, ids, context=context):
            if partner.name_official:
                res[partner.id] = partner.name_official
            elif partner.parent_id and partner.parent_id.name_official:
                res[partner.id] = partner.parent_id.name_official
            else:
                res[partner.id] = partner.name
        return res

    def _get_address_multi(self, cr, uid, ids, field, arg, context=None):
        res = {}
        for partner in self.browse(cr, uid, ids, context=context):
            real_partner = partner.parent_id if partner.use_parent_address else partner
            res[partner.id] = real_partner.address_formatted
        return res

    _name = 'res.partner'
    _inherit = 'res.partner'
    _columns = {
        'name_official': fields.char('Official name', size=200),
        'name_official_multi': fields.function(_get_official_name_multi, type='char'),
        'inn': fields.char('INN', size=12),
        'kpp': fields.char('KPP', size=9),
        'okpo': fields.char('OKPO', size=14),
        'contract_num': fields.char('Contract number', size=64),
        'contract_date': fields.date('Contract date'),
        'ceo': fields.char('CEO', size=200, help="Example: Lenin V.I."),
        'ceo_function': fields.char('CEO Function', size=200),
        'accountant': fields.char('Chief accountant', size=200),
        'address_formatted': fields.function(_format_address, string='Formatted Address', type='char', store=False),
        'address_multi': fields.function(_get_address_multi, type='char'),
    }
res_partner()


class Bank(osv.osv):
    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=80):
        if not args:
            args = []
        ids = self.search(cr, uid, ['|', ('bic', operator, name),
                                        ('name', operator, name)] + args, limit=limit, context=context)
        return self.name_get(cr, uid, ids)

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

        #643 - Российская федерация
        ru_id = self.pool.get('res.country').search(cr, uid,
                                                    [('numeral_code', '=', 643)],
                                                    context=context)[0]
        bic_list = get_bic_list()
        for bic in bic_list.values():
            context['active_test'] = False
            bic['country'] = ru_id
            ids = bank.search(cr, uid, [('bic', '=', bic['bic'])], context=context)
            if ids:
                bank.write(cr, uid, ids, bic, context=context)
            else:
                bank.create(cr, uid, bic, context=context)

        return {
            'view_type': 'form,tree',
            'view_mode': 'tree',
            'res_model': 'res.bank',
            'type': 'ir.actions.act_window',
        }

    _name = 'wizard.update.banks'

wizard_update_banks()


class product_product(osv.osv):
    _inherit = 'product.product'
    _name = 'product.product'
    _columns = {
        'country_origin_id': fields.many2one('res.country', string="Country of origin"),
        'declaration_code': fields.char('Declaration code'),
    }


class res_country(osv.osv):
    _name = 'res.country'
    _inherit = 'res.country'
    _columns = {
        'numeral_code': fields.integer("Numeral country code"),
        'full_name': fields.char("Full name"),
    }


class res_currency(osv.osv):
    _name = 'res.currency'
    _inherit = 'res.currency'
    _columns = {
        'code': fields.integer("Code"),
        'full_name': fields.char("Full name"),
    }


class product_uom(osv.osv):
    _name = 'product.uom'
    _inherit = 'product.uom'
    _columns = {
        'okei': fields.integer('OKEI'),
        'full_name': fields.char('Full name', size=128),
    }
