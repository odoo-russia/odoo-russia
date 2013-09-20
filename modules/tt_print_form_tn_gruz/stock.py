# coding: utf-8
from openerp.osv import osv, fields


def _get_invoices_count(self, cr, uid, ids, field, arg, context=None):
    res = {}
    for row in self.browse(cr, uid, ids, context):
        res[row.id] = len(row.move_lines)
    return res


# 'cargo_description' - Наименование груза
# 'cargo_mark' - маркировка груза
# 'cargo_volume' - объём/масса груза

columns = {
    'cargo_description': fields.char("Description of cargo"),
    'cargo_mark': fields.char('Cargo mark'),
    'cargo_volume': fields.char('Cargo volume'),
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