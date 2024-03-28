from odoo import fields,api,models
from  datetime import datetime
class TechnicalOrder(models.Model):
    _name='technical.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "Request_name"
    Sequence=fields.Char()
    Request_name=fields.Char(required=True)
    requested_by=fields.Many2one('res.users',default=lambda self: self.env.user,required=True)
    customer=fields.Many2one('res.partner')
    startDate = fields.Date(default=lambda self: datetime.today().date())
    endDate = fields.Date()
    RejectionReason=fields.Char(readonly=True)
    TotalPrice = fields.Float(readonly=True, compute='_compute_total_order_price', store=True)
    technical_order_lines_id = fields.One2many('technical.order.line','technical_order_id')
    state = fields.Selection([
        ('draft', "Draft"),
        ('approved', 'Approved'),
        ('reject', 'Reject'),
        ('cancel', 'Cancel'),
        ('to_be_approved', 'to be Approved'),
    ], default='draft')
    remaining=fields.Integer(readonly=True,default=1)
    sale_order_id = fields.One2many('sale.order', 'technical_order')
    technical_count = fields.Integer("Real Count", compute="compute_technical_count")
    @api.depends('technical_order_lines_id.Total')
    def _compute_total_order_price(self):
      for order in self:
        order.TotalPrice = sum(order.technical_order_lines_id.mapped('Total'))

    def action_submit_for_approval(self):
        self.state = 'to_be_approved'

    def action_approve(self):
        self.ensure_one()
        self.state = 'approved'

        # Get the technical manager group

        technical_managers_group = self.env.ref('store.technical_order_manager_group')
        technical_managers = technical_managers_group.users

        # Constructing the subject and body of the email
        subject = f"Purchase Request {self.Request_name} Approved"
        body = f"Purchase Request {self.Request_name} has been approved."

        # Send email notification to all users in the purchase manager group
        for manager in technical_managers:
            mail_vals = {
                'subject': subject,
                'body_html': body,
                'email_to': manager.email,
            }
            self.env['mail.mail'].create(mail_vals).send()

            # Create a log note for each manager in the manager group
            self.message_post(
                body=body,
                subject=subject,
                partner_ids=[manager.partner_id.id],  # Use a command to add the manager as a recipient
                subtype_id=self.env.ref('mail.mt_note').id,  # Use subtype 'Note'
            )
        return True

    def action_cancle(self):
        self.state = 'cancel'

    def action_rejection_reason(self):
        self.state = 'reject'

    def action_reset_to_draft(self):
        self.state = 'draft'
    def action_SO(self):
        order_lines = []
        for line in self.technical_order_lines_id:
            sumition = 0
            if line.sale_order_id:
              for sale_order_line in  line.sale_order_id:
                if sale_order_line.state=='sale' :
                  sumition +=sale_order_line.product_uom_qty
              quantity = line.quantity - sumition
              if quantity<=0:
                 line.rem=0
                 quantity=0
              else:
                  line.rem=quantity
              self.remaining=quantity
            else:
                quantity=line.quantity
            order_lines.append((0, 0, {
                'technical_order_id':line.id,
                'product_id': line.product_id.id,
                'product_uom_qty': quantity,
                'price_unit': line.Price,
                'name': line.Description,
                'price_subtotal': line.Total,
                'size': line.size,

            }))

        self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'technical_order': self.id,
            'order_line': order_lines,
        })




    @api.model
    def create(self, vals):
        result = super(TechnicalOrder, self).create(vals)

        result['Sequence'] = self.env['ir.sequence'].next_by_code(
                'seq.technical.order')
        return result

    def compute_technical_count(self):
        for rec in self:
            rec.technical_count = self.env['sale.order'].search_count([('technical_order', '=', rec.id)])
    def action_open_no_so(self):
        return {
            'name': 'Technical order ',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('technical_order', '=', self.id)],
        }


class ResPartnersInherit(models.Model):
    _inherit = 'res.partner'
    is_tech_offer=fields.Boolean()

class TechnicalOrderLine(models.Model):
    _name ='technical.order.line'
    product_id=fields.Many2one('product.product',required=True)
    Description=fields.Text(compute='_compute_description')
    sale_order_id = fields.One2many('sale.order.line','technical_order_id')
    quantity = fields.Integer(default=1)
    Price = fields.Float(string='Product Price ', readonly=True, related='product_id.lst_price', store=True)
    Total = fields.Float(readonly=True, compute='_compute_total_product_cost')
    technical_order_id=fields.Many2one('technical.order')
    rem=fields.Integer(default=lambda self: self.quantity)
    size = fields.Integer()
    @api.depends('product_id')
    def _compute_description(self):
      for line in self:
        line.Description = line.product_id.name

    @api.depends('Price','quantity')
    def _compute_total_product_cost(self):
        for lin in self:
            lin.Total=lin.Price*lin.quantity
    @api.onchange('quantity')
    def remainain_defualt(self):
        self.rem=self.quantity

