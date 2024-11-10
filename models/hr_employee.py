from odoo import api,fields,models,exceptions
from odoo.osv import expression  # Import expression module
from odoo.exceptions import ValidationError

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    github_account = fields.Char(string="GitHub Account")
    project_ids = fields.One2many('project.collaborator', 'employee_id', string="Projects")

    def toggle_active(self):
        # Check if the employee is active in any project before proceeding with archiving
        active_project_collaborators = self.env['project.collaborator'].search([
            ('employee_id', 'in', self.ids),
            ('status', '=', 'active')
        ])

        if active_project_collaborators:
            raise ValidationError(
                "One or more of the selected employees cannot be archived because they are still active in a project. Please deactivate their status in the project first."
            )

        # Call the original toggle_active method to keep the original logic
        res = super(HrEmployee, self).toggle_active()

        # For unarchived employees, clear departure details
        unarchived_employees = self.filtered(lambda employee: employee.active)
        unarchived_employees.write({
            'departure_reason_id': False,
            'departure_description': False,
            'departure_date': False
        })

        # For archived employees, toggle home address if inactive
        archived_addresses = unarchived_employees.mapped('address_home_id').filtered(lambda addr: not addr.active)
        archived_addresses.toggle_active()

        archived_employees = self.filtered(lambda e: not e.active)
        if archived_employees:
            # Empty links to this employee (example: manager, coach, time off responsible, ...)
            employee_fields_to_empty = self._get_employee_m2o_to_empty_on_archived_employees()
            user_fields_to_empty = self._get_user_m2o_to_empty_on_archived_employees()
            employee_domain = [[(field, 'in', archived_employees.ids)] for field in employee_fields_to_empty]
            user_domain = [[(field, 'in', archived_employees.user_id.ids) for field in user_fields_to_empty]]
            employees = self.env['hr.employee'].search(expression.OR(employee_domain + user_domain))
            for employee in employees:
                for field in employee_fields_to_empty:
                    if employee[field] in archived_employees:
                        employee[field] = False
                for field in user_fields_to_empty:
                    if employee[field] in archived_employees.user_id:
                        employee[field] = False

        # If only one employee is being archived and no wizard flag is set, show the departure wizard
        if len(self) == 1 and not self.active and not self.env.context.get('no_wizard', False):
            return {
                'type': 'ir.actions.act_window',
                'name': _('Register Departure'),
                'res_model': 'hr.departure.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'active_id': self.id},
                'views': [[False, 'form']]
            }

        return res