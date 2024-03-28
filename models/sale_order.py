from odoo import  api,fields,models,exceptions

class SaleOrderLineinherit(models.Model):
    _inherit='sale.order'
    technical_order=fields.Many2one('technical.order')

    def create_transfer(self):
        for order in self:
            for line in order.order_line:
                self.env['stock.move'].create({
                    'size': line.size,
                    'name':line.name,
                    'product_id':line.product_id.id,
                    'product_uom':1,
                    'price_unit':line.price_unit,
                    'product_uom_qty':line.product_uom_qty,
                    'location_id':1,
                    'location_dest_id':1,
                    'procure_method':'make_to_stock'
                })



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


