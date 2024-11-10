from odoo import api,fields,models


class AccountMovieLine(models.Model):
    _inherit='account.move.line'
    size = fields.Integer()
