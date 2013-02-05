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

class res_partner(osv.osv):
    def get_payment_term_id(self, cr, uid, vals, payment_deferment, prepayment_percentage, context):
        if payment_deferment:
            pterm_name = '%d Days' % payment_deferment
            if prepayment_percentage:
                pterm_name = ', '.join((pterm_name, '%.2f%% Advance' % prepayment_percentage))
        else:
            pterm_name= 'Immediate Payment'
        args = [('name', '=', pterm_name)]
        res = self.pool.get('account.payment.term').search(cr, uid, args, context=context)
        if res:
            pterm_id = res[0]
        else:
            context_en = context.copy()
            context_en['lang'] = 'en_US'
            pterm_vals = {
                'name': pterm_name,
                }
            pterm_id = self.pool.get('account.payment.term').create(cr, uid, pterm_vals, context=context_en)
            if pterm_id:
                if prepayment_percentage:
                    pterm_line_vals = {
                        'value': 'procent',
                        'value_amount': prepayment_percentage / 100.00,
                        'days': 0,
                        'days2': 0,
                        'payment_id': pterm_id,
                    }
                    self.pool.get('account.payment.term.line').create(cr, uid, pterm_line_vals, context=context)
                pterm_line_vals = {
                    'value': 'balance',
                    'days': payment_deferment,
                    'days2': 0,
                    'payment_id': pterm_id,
                    }
                self.pool.get('account.payment.term.line').create(cr, uid, pterm_line_vals, context=context)
        return pterm_id

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        payment_deferment = vals.get('payment_deferment', False)
        prepayment_percentage = vals.get('prepayment_percentage', False)
        vals['property_payment_term'] = self.get_payment_term_id(cr, uid, vals, payment_deferment,
                                                                     prepayment_percentage, context=context)
        return super(res_partner, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        res_common = True
        if isinstance(ids, (int, long)):
            ids = [ids]
        for partner in self.browse(cr, uid, ids, context):
            payment_deferment = vals.get('payment_deferment')
            prepayment_percentage = vals.get('prepayment_percentage')
            if payment_deferment or prepayment_percentage:
                if payment_deferment is None:
                    payment_deferment = self.browse(cr, uid, partner.id, context).payment_deferment
                if prepayment_percentage is None:
                    prepayment_percentage = self.browse(cr, uid, partner.id, context).prepayment_percentage
                vals['property_payment_term'] = self.get_payment_term_id(cr, uid, vals, payment_deferment,
                                                                         prepayment_percentage, context=context)
            res = super(res_partner, self).write(cr, uid, partner.id, vals, context=context)
            res_common = res_common and res
        return res_common


    _name = 'res.partner'
    _inherit = 'res.partner'
    _columns = {
        'contract_expiration_date': fields.date('Contract expiration date'),
        'payment_deferment': fields.integer('Deferment of payment'),
        'prepayment_percentage': fields.float('Prepayment percentage', digits=(4,2)),
    }
res_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: