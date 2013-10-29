# coding: utf-8
from openerp.osv import osv, fields


def _get_invoices_count(self, cr, uid, ids, field, arg, context=None):
    res = {}
    for row in self.browse(cr, uid, ids, context):
        res[row.id] = len(row.move_lines)
    return res

columns = {
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
    'invoices_count': fields.function(_get_invoices_count, type='integer'),
}


class stock_picking(osv.osv):
    _name = 'stock.picking'
    _inherit = 'stock.picking'
    _columns = columns
stock_picking()


class stock_picking_in(osv.osv):
    _name = 'stock.picking.in'
    _inherit = 'stock.picking.in'
    _columns = columns
stock_picking_in()


class stock_picking_out(osv.osv):
    _name = 'stock.picking.out'
    _inherit = 'stock.picking.out'
    _columns = columns
stock_picking_out()