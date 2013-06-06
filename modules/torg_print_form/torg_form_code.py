# -*- coding: utf-8 -*-

import time
from openerp.report import report_sxw
from osv import orm, osv, fields
from openerp.addons.jasper_reports.pytils import numeral

class torg_form(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(torg_form, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {'time': time,})

report_sxw.report_sxw('report.new_torg_form_report', 'account.invoice',
                      'torg_print_form/torg12.jrxml',
                      parser=torg_form)

class account_invoice(osv.osv):

    def _get_pos_in_words(self,cr,uid,ids,field,arg,context=None):
        res = {}

        for row in self.browse(cr, uid, ids, context):

            print 1

        return res
    _name = 'account.invoice'
    _inherit = 'account.invoice'
    _columns = {
        'pos_in_words': fields.function(_get_pos_in_words, type='char'),
    }
account_invoice()