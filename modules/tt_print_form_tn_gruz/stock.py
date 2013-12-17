# coding: utf-8
import re
from datetime import datetime
from openerp.osv import osv, fields

account_number_re = re.compile(r"[a-zA-Zа-яА-Я]*\/[0-9]*\/([0-9]*)", re.I + re.U)

PICKING_MAP = {
    'stock.picking': 'Picking INT',
    'stock.picking.in': 'Picking IN',
    'stock.picking.out': 'Picking OUT',
}


def _get_number_only(self, cr, uid, ids, field_name, arg, context):
    res = {}
    seq_obj = self.pool.get('ir.sequence')

    for row in self.browse(cr, uid, ids, context):
        number = u'0-черновик'
        seq_name = PICKING_MAP.get(self._name, 'Picking INT')
        seq_id = seq_obj.search(cr, uid, ['|', ('code', '=', self._name),
                                          ('name', '=', seq_name)], context=context)
        seq_id = seq_id and seq_id[0] or False

        if seq_id and row.name:
            seq_data = seq_obj.read(cr, uid, seq_id, ['padding'], context=context)
            padding = seq_data.get('padding')
            padding = 0 - int(padding)
            number = row.name[padding:].lstrip('0')
        res[row.id] = number
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