# import openerp.addons.web.http as http
# # from openerp.addons.web.http import request
# import openerp.addons.web.controllers.main as main

import openerp.addons.web.http as openerpweb
import openerp.addons.web.controllers.main as main

import base64
import simplejson
import time
import zlib

# from openerp.addons.web import http
# openerpweb = http


class Report(main.Reports):
    _cp_path = "/web/report"

    def __init__(self):
        print 'init controller'

    @openerpweb.httprequest
    def index(self, req, action, token):
        action = simplejson.loads(action)

        report_srv = req.session.proxy("report")
        context = dict(req.context)
        context.update(action["context"])

        report_data = {}
        report_ids = context["active_ids"]
        if 'report_type' in action:
            report_data['report_type'] = action['report_type']
        if 'datas' in action:
            if 'ids' in action['datas']:
                report_ids = action['datas'].pop('ids')
            report_data.update(action['datas'])

        report_id = report_srv.report(
            req.session._db, req.session._uid, req.session._password,
            action["report_name"], report_ids,
            report_data, context)

        report_struct = None
        while True:
            report_struct = report_srv.report_get(
                req.session._db, req.session._uid, req.session._password, report_id)
            if report_struct["state"]:
                break

            time.sleep(self.POLLING_DELAY)

        report = base64.b64decode(report_struct['result'])
        if report_struct.get('code') == 'zlib':
            report = zlib.decompress(report)
        report_mimetype = self.TYPES_MAPPING.get(
            report_struct['format'], 'octet-stream')
        file_name = action.get('name', 'report')
        if 'name' not in action:
            reports = req.session.model('ir.actions.report.xml')
            res_id = reports.search([('report_name', '=', action['report_name']),],
                                    0, False, False, context)
            if len(res_id) > 0:
                file_name = reports.read(res_id[0], ['name'], context)['name']
            else:
                file_name = action['report_name']
        # file_name = '%s.%s' % (file_name, report_struct['format'])
        file_name = "oisdhgouisdhiouhgij.pdf"

        return req.make_response(report,
             headers=[
                 ('Content-Disposition', main.content_disposition(file_name, req)),
                 ('Content-Type', report_mimetype),
                 ('Content-Length', len(report))],
             cookies={'fileToken': token})
