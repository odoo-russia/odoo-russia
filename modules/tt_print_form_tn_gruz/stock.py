# coding: utf-8
from openerp.osv import osv, fields


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

def _get_invoices_count(self, cr, uid, ids, field, arg, context=None):
    res = {}
    for row in self.browse(cr, uid, ids, context):
        res[row.id] = len(row.move_lines)
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

    'gruz_notes_one': fields.text(''),
    'gruz_notes_two': fields.text(''),
    'gruz_notes_three': fields.text(''),
    'gruz_notes_four': fields.text(''),

    'gruz_others_one': fields.text(''),
    'gruz_others_two': fields.text(''),

    'gruz_readdressing_one': fields.text(''),
    'gruz_readdressing_two': fields.text(''),
    'gruz_readdressing_three': fields.text(''),
    'gruz_readdressing_four': fields.text(''),

    'gruz_cost_two': fields.text(''),

    'invoices_count': fields.function(_get_invoices_count, type='integer'),
    'number_only': fields.function(_get_number_only, type="char"),
    'cost_total': fields.function(_get_cost_total, type='float')
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