# -*- coding: utf-8 -*-

import time
from openerp.report import report_sxw
from osv import orm, osv, fields

class torg_form(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(torg_form, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {'time': time,})

report_sxw.report_sxw('report.new_torg_form_report', 'account.invoice',
                      'torg_print_form/torg12.jrxml',
                      parser=torg_form)