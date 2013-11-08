# coding: utf-8
import re
from datetime import datetime
from openerp.osv import osv, fields

account_number_re = re.compile(r"[a-zA-Zа-яА-Я]*\/[0-9]*\/([0-9]*)", re.I + re.U)


def _get_number_only(self, cr, uid, ids, field_name, arg, context=None):
    res = {}

    for row in self.browse(cr, uid, ids, context=context):
        seq_id = self.pool.get('ir.sequence').search(cr, uid, [('code', '=', self._name)], context=context)
        sequence = self.pool.get('ir.sequence').read(cr, uid, seq_id, ['padding', 'active'], context=context)[0]
        if sequence and sequence.get('active'):
            padding = sequence.get('padding')
            padding = 0 - int(padding)
            res[row.id] = row.name[padding:].lstrip('0')

    return res


def _get_cost_total(self, cr, uid, ids, field_name, arg, context=None):
    res = {}

    for row in self.browse(cr, uid, ids, context=context):
        res[row.id] = 0
        for line in row.move_lines:
            res[row.id] += line.product_id.list_price * line.product_qty
    return res


def _get_weight_total(self, cr, uid, ids, field_name, arg, context=None):
    res = {}
    for picking in self.browse(cr, uid, ids, context=context):
        weight_total = 0
        for move in picking.move_lines:
            weight_total += move.product_id.weight_net * move.product_qty
        res[picking.id] = weight_total
    return res


def _get_pickings_count(self, cr, uid, ids, field, arg, context=None):
    res = {}
    for row in self.browse(cr, uid, ids, context):
        res[row.id] = len(row.move_lines)
    return res


def _get_invoices_string(self, cr, uid, ids, field_name, arg, context=None):
    result = {}
    for picking in self.browse(cr, uid, ids, context=context):
        invoices = []
        for invoice in picking.gruz_invoice_ids:
            if invoice.number:
                match = account_number_re.findall(invoice.number)
                if match:
                    date = ''
                    if invoice.date_invoice:
                        date = datetime.strftime(datetime.strptime(invoice.date_invoice, '%Y-%m-%d'), 'от %d.%m.%Y г.')
                    invoices.append(u"Накладная №%s %s" % (match[0].lstrip('0'), unicode(date, 'utf')))
        result[picking.id] = ', '.join(invoices)
    return result


def _get_supp_docs(self, cr, uid, ids, field_name, arg, context=None):
    res = {}
    for picking in self.browse(cr, uid, ids, context=context):
        docs = []
        if picking.gruz_attached_invoices:
            docs.append(picking.gruz_attached_invoices)
        if picking.gruz_supp_docs_one:
            docs.append(picking.gruz_supp_docs_one)
        res[picking.id] = ', '.join(docs)
    return res


def _get_partner_name(self, cr, uid, ids, field_name, arg, context=None):
    res = dict.fromkeys(ids)

    for picking in self.browse(cr, uid, ids, context=context):
        partner = picking.partner_id

        if partner.name_official:
            res[picking.id] = partner.name_official
        elif partner.parent_id and partner.parent_id.name_official:
            res[picking.id] = partner.parent_id.name_official
        else:
            res[picking.id] = partner.name
    return res


def _get_partner_address(self, cr, uid, ids, field_name, arg, context=None):
    res = dict.fromkeys(ids)

    for picking in self.browse(cr, uid, ids, context=context):
        partner = partner.parent_id if partner.use_parent_address else partner
        res[picking.id] = partner.address_formatted
    return res


columns = {
    'gruz_shipper_three': fields.text(''),

    'gruz_consignee_three': fields.text(''),

    'gruz_goods_name_one': fields.text(''),
    'gruz_goods_name_two': fields.text(''),
    'gruz_goods_name_three': fields.text(''),
    'gruz_goods_name_four': fields.text(''),

    'gruz_supp_docs_one': fields.text(''),
    'gruz_supp_docs_two': fields.text(''),

    'gruz_shipper_instructions_one': fields.text(''),
    'gruz_shipper_instructions_two': fields.text(''),
    'gruz_shipper_instructions_three': fields.text(''),

    'gruz_carry_conditions_one': fields.text(''),
    'gruz_carry_conditions_two': fields.text(''),
    'gruz_carry_conditions_three': fields.text(''),
    'gruz_carry_conditions_four': fields.text(''),
    'gruz_carry_conditions_five': fields.text(''),
    'gruz_carry_conditions_six': fields.text(''),

    'gruz_order_acceptance': fields.text(''),

    'gruz_carrier_one': fields.text(''),
    'gruz_carrier_two': fields.text(''),
    'gruz_carrier_three': fields.text(''),
    'gruz_carrier_four': fields.text(''),
    'gruz_carrier_five': fields.text(''),

    'gruz_vehicle_one': fields.text(''),
    'gruz_vehicle_two': fields.text(''),

    'gruz_others_one': fields.text(''),
    'gruz_others_two': fields.text(''),

    'gruz_readdressing_one': fields.text(''),
    'gruz_readdressing_two': fields.text(''),
    'gruz_readdressing_three': fields.text(''),
    'gruz_readdressing_four': fields.text(''),

    'gruz_cost_two': fields.text(''),

    'pickings_count': fields.function(_get_pickings_count, type='integer'),
    'number_only': fields.function(_get_number_only, type='char'),
    'cost_total': fields.function(_get_cost_total, type='float'),
    'weight_total': fields.function(_get_weight_total, type='float'),
    'gruz_invoice_ids': fields.many2many('account.invoice', domain="[('origin', '=', origin), "
                                                                   "('state', 'in', ['open', 'paid'])]"),
    'gruz_attached_invoices': fields.function(_get_invoices_string, type='char'),
    'gruz_supp_docs': fields.function(_get_supp_docs, type='char'),

    'partner_name': fields.function(_get_partner_name, type='char'),
    'partner_address': fields.function(_get_partner_address, type='char'),
}


class stock_picking(osv.osv):
    _name = 'stock.picking'
    _inherit = 'stock.picking'
    _columns = columns
stock_picking()


class stock_picking_out(osv.osv):
    _name = 'stock.picking.out'
    _inherit = 'stock.picking.out'
    _columns = columns
stock_picking_out()