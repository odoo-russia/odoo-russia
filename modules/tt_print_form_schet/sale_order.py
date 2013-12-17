# coding: utf-8
from openerp.osv import osv, fields
from openerp.addons.jasper_reports.pytils import numeral, dt


class sale_order(osv.osv):
    _name = 'sale.order'
    _inherit = 'sale.order'

    def _is_invoice(self, cr, uid, ids, field, arg, context=None):
        res = {}
        for row in self.browse(cr, uid, ids, context):
            res[row.id] = False
        return res

    def _get_number_only(self, cr, uid, ids, field_name, arg, context):
        res = {}
        seq_obj = self.pool.get('ir.sequence')

        for row in self.browse(cr, uid, ids, context):
            number = u'0-черновик'
            seq_id = seq_obj.search(cr, uid, ['|', ('code', '=', self._name),
                                              ('name', '=', 'Sales Order')], context=context)
            seq_id = seq_id and seq_id[0] or False

            if seq_id and row.name:
                seq_data = seq_obj.read(cr, uid, seq_id, ['padding'], context=context)
                padding = seq_data.get('padding')
                padding = 0 - int(padding)
                number = row.name[padding:].lstrip('0')
            res[row.id] = number
        return res

    def _get_price_in_words(self, cr, uid, ids, field_name, arg, context):
        res = {}

        for row in self.browse(cr, uid, ids, context):
            rubles = numeral.rubles(int(row.amount_total))
            copek_num = round((row.amount_total - int(row.amount_total))*100)
            copek = numeral.choose_plural(int(copek_num), (u"копейка", u"копейки", u"копеек"))
            res[row.id] = ("%s %02d %s")%(rubles, copek_num, copek)

        return res

    def _get_orders_count(self, cr, uid, ids, field, arg, context=None):
        res = {}

        for row in self.browse(cr, uid, ids, context):
            res[row.id] = len(row.order_line)

        return res

    def _get_report_date_formatted(self, cr, uid, ids, field, args, context=None):
        res = {}
        for row in self.browse(cr, uid, ids, context=context):
            from datetime import datetime
            from openerp.tools.misc import DEFAULT_SERVER_DATE_FORMAT as date_format
            date = row.date_invoice or fields.date.today()
            date_object = datetime.strptime(date, date_format).date()
            res[row.id] = dt.ru_strftime(format=u"%d %B %Y", date=date_object, inflected=True)
        return res

    _columns = {
        'is_invoice': fields.function(_is_invoice, type='boolean'),
        'number_only': fields.function(_get_number_only, type='char'),
        'price_in_words':fields.function(_get_price_in_words, type='char'),
        'orders_count': fields.function(_get_orders_count, type='integer'),
        'report_date_formatted': fields.function(_get_report_date_formatted, type='char'),
    }
sale_order()