from openerp.osv import osv, fields
from tools.translate import _


class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"

    def _check_needed_qty(self, cr, uid, ids, context=None):
        stock_move_obj = self.pool.get('stock.move')

        for picking in self.browse(cr, uid, ids, context=context):
            message = stock_move_obj._check_available_quantity(cr, uid, [move.id for move in picking.move_lines], context=context)
            if message:
                string = '\n'.join(message)
                if context.get('mute'):
                    return True
                raise osv.except_osv(_('Not enough products: '), string)
        return False

    def test_assigned(self, cr, uid, ids):
        if self._check_needed_qty(cr, uid, ids, {'mute': True}):
            return False
        return super(stock_picking, self).test_assigned(cr, uid, ids)
stock_picking()


class stock_move(osv.osv):
    _name = "stock.move"
    _inherit = "stock.move"

    def action_done(self, cr, uid, ids, context=None):
        self._get_missed_products(cr, uid, ids, context=context)
        return super(stock_move, self).action_done(cr, uid, ids, context)

    def force_assign(self, cr, uid, ids, context=None):
        self._get_missed_products(cr, uid, ids, context=context)
        return super(stock_move, self).force_assign(cr, uid, ids, context=context)

    def _get_missed_products(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        res = self._check_available_quantity(cr, uid, ids, context)
        if res:
            raise osv.except_osv(_('Not enough products: '), '\n'.join(res))

    def _check_available_quantity(self, cr, uid, ids, context=None):
        res = []
        if context is None:
            context = {}

        for move in self.browse(cr, uid, ids, context=context):
            message = self._get_product_needed_qty(cr, uid, move.id, context=context)
            if message:
                res.append(message)

        return res

    def _get_product_needed_qty(self, cr, uid, move_line_id, context=None):
        message = None
        if context is None:
            context = {}

        line = self.browse(cr, uid, move_line_id, context=context)
        if not self._is_location_internal(cr, uid, move_line_id, context=context):
            return None

        if line.location_id.id == line.location_dest_id.id:
            return None

        if line.state in ('done', 'cancel'):
            return None

        requested = line.product_qty
        location = line.location_id

        c = {
            'lang': context.get('lang', False),
            'location': location.id,
            'compute_child': True
        }

        product = self.pool.get('product.product').browse(cr, uid, line.product_id.id, context=c)
        if product.type == 'product':
            available = product.qty_available

            if line.state != 'assigned':
                confirmed_moves = self.search(cr, uid, [('product_id', '=', line.product_id.id),
                                                        ('state', '=', 'assigned'),
                                                        ('location_id', '=', line.location_id.id)])
                confirmed_sum = 0.0
                for move in self.browse(cr, uid, confirmed_moves, context):
                    if move.location_id != move.location_dest_id:
                        confirmed_sum += move.product_qty
                available -= confirmed_sum

            message = None
            if round(available, 3) < round(requested, 3):
                needed_qty = min((requested - available), requested)
                if not needed_qty % 1:
                    needed_qty = int(needed_qty)
                message = (_("%s [%s %s] in location %s")) % (line.product_id.name,
                                                              str(needed_qty),
                                                              line.product_id.uom_id.name,
                                                              location.name)
        return message

    def _is_location_internal(self, cr, uid, id, context=None):
        """
        :return: True - If move is internal or if in source location internal location. Else - False.
        """
        res = False
        if context is None:
            context = {}

        move = self.browse(cr, uid, id, context=context)
        if 'picking_type' in context:
            res = False if context['picking_type'] == 'in' else True

        if move.picking_id:
            res = False if move.picking_id.type == 'in' else True
        elif move.location_id and move.location_id.usage:
            res = True if move.location_id.usage == 'internal' else False

        return res
stock_move()
