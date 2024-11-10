from odoo import fields,api,models

class ProjectTask(models.Model):
    _inherit = 'project.task'

    developer_id = fields.Many2one('hr.employee', string="Developer")
    functional_consultant_id = fields.Many2one('hr.employee', string="Functional Consultant")
    development_status = fields.Selection([
        ('pending', 'Pending'),
        ('ongoing', 'Ongoing'),
        ('delivered', 'Delivered'),
        ('onhold', 'On Hold'),
        ('cancelled', 'Cancelled')
    ], string="Development Status")
    module = fields.Char(string="Module")
    branch = fields.Char(string="Branch")
    release_notes = fields.Text(string="Release Notes")
    custom_priority = fields.Selection([('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], string="Priority")
    internal_deadline = fields.Date(string="Internal Deadline")

    # Allocated Times
    research_solution_time = fields.Float(string="Research & Solution Design", widget='time')
    development_time = fields.Float(string="Development Time", widget='time')
    testing_time = fields.Float(string="Testing Time", widget='time')
    allocated_time = fields.Float(string="Total Allocated Time", compute='_compute_allocated_time', store=True)

    task_number = fields.Char(string="Task Number", readonly=True)

    @api.depends('research_solution_time', 'development_time', 'testing_time')
    def _compute_allocated_time(self):
        for task in self:
            task.allocated_time = task.research_solution_time + task.development_time + task.testing_time

    @api.model
    def create(self, vals):
        vals['task_number'] = self.env['ir.sequence'].next_by_code('project.task.number')
        return super().create(vals)


