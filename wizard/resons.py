from odoo import fields,api,models

class RejectionReasons(models.TransientModel):
    _name='rejection.reason'
    name=fields.Char(required=True)

    def action_add_rejection(self):
       active_id = self.env.context.get('active_id')

       current_technical_order = self.env['technical.order'].search([('id', '=', active_id)])
       current_technical_order.RejectionReason = self.name
       current_technical_order.state='reject'