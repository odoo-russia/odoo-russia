#import wizard
import pooler
import base64
from osv import osv,fields
from tools.translate import _

class create_data_template(osv.osv_memory):
    _name = 'jasper.create.data.template'
    _description = 'Create data template'

    def action_create_xml(self, cr, uid, ids, context=None):
        for data in  self.read(cr, uid, ids, context=context):
            model = self.pool.get('ir.model').browse(cr, uid, data['model'][0], context=context)
            xml = self.pool.get('ir.actions.report.xml').create_xml(cr, uid, model.model, data['depth'], context)
            self.write(cr,uid,ids,{
                'data' : base64.encodestring( xml ), 
                'filename': 'template.xml'
            })
        return {
            'view_type': 'form,tree',
            'view_mode': 'form',
            'res_model': 'jasper.create.data.template',
            'res_id': ids[0],
            'targer': 'new',
            'type': 'ir.actions.act_window',
            }

    _columns = {
        'model': fields.many2one('ir.model', 'Model', required=True),
        'depth': fields.integer("Depth", required=True),
        'filename': fields.char('File Name', size=32),
        'data': fields.binary('XML')
    }

    _defaults = {
        'depth': 1
    }    
create_data_template()
