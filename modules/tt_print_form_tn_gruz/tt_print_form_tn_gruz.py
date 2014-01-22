# -*- coding: utf-8 -*-

import time
from openerp.report import report_sxw


class waybill_report_stock(report_sxw.rml_parse):
    name = 'stock_picking.new_waybill_report'

    def __init__(self, cr, uid, name, context):
        super(waybill_report_stock, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time})

#report_sxw.report_sxw('report.new_waybill_report_stock', 'stock_picking',
#                      'tt_print_form_tn_gruz/nakl_transp.jrxml',
#                      parser=waybill_report_stock)


class waybill_report_stock_in(report_sxw.rml_parse):
    name = 'stock_picking_in.new_waybill_report'

    def __init__(self, cr, uid, name, context):
        super(waybill_report_stock_in, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time})

#report_sxw.report_sxw('report.new_waybill_report_stock_in', 'stock_picking_in',
#                      'tt_print_form_tn_gruz/nakl_transp.jrxml',
#                      parser=waybill_report_stock_in)


class waybill_report_stock_out(report_sxw.rml_parse):
    name = 'stock_picking_out.new_waybill_report'

    def __init__(self, cr, uid, name, context):
        super(waybill_report_stock_out, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time})

#report_sxw.report_sxw('report.new_waybill_report_stock_out', 'stock_picking_out',
#                      'tt_print_form_tn_gruz/nakl_transp.jrxml',
#                      parser=waybill_report_stock_out)


