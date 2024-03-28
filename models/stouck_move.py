from odoo import api,fields,models

class StockMovie(models.Model):
    _inherit='stock.move'
    size=fields.Integer()
