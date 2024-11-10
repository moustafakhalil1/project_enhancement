from odoo import  api,fields,models,exceptions

class ProjectCollaborator(models.Model):
    _name = 'project.collaborator'
    _description = 'Project Collaborator'

    project_id = fields.Many2one('project.project', string="Project", ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    status = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')], string="Status", default='active')


    def toggle_status(self):
        for record in self:
            record.status = 'inactive' if record.status == 'active' else 'active'
