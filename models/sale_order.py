from odoo import  api,fields,models,exceptions

class SaleOrderLineinherit(models.Model):
    _inherit='sale.order'
    technical_order=fields.Many2one('technical.order')

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            for line in order.order_line:
                for move in line.move_ids:
                    move.write({
                        'size': line.size
                    })
        return res



class SaleOrderLineinherit(models.Model):
    _inherit='sale.order.line'
    technical_order_id=fields.Many2one('technical.order.line')
    size=fields.Integer()
    def write(self, vals):
        # Check if the quantity is being changed
        if 'product_uom_qty' in vals:
            for line in self:
                # Get the corresponding Technical Order line
                technical_line = line.technical_order_id
                if technical_line :
                    # Check if the new quantity exceeds the one requested in the Technical Order
                    if vals['product_uom_qty'] > technical_line.rem:
                        raise exceptions.ValidationError(
                            "Quantity can't exceed the one requested in the Technical Order")

        return super(SaleOrderLineinherit, self).write(vals)

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLineinherit, self)._prepare_invoice_line()
        res.update({'size': self.size})
        return res


