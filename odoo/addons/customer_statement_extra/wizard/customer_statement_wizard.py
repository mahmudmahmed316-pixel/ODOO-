from odoo import models, fields, api

class CustomerStatementWizard(models.TransientModel):
    _name = 'customer.statement.wizard'
    _description = 'Customer Statement Wizard'

    name = fields.Char(default="Customer Statement Recap")
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    sales_count = fields.Integer(related='partner_id.customer_sales_count')
    total_sales_amount = fields.Monetary(related='partner_id.customer_total_sales_amount', currency_field='currency_id')
    total_payments_amount = fields.Monetary(related='partner_id.total_payments_amount', currency_field='currency_id')
    balance = fields.Monetary(related='partner_id.customer_balance', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='partner_id.currency_id')

    sale_order_ids = fields.Many2many('sale.order', string='Sales Details')
    payment_ids = fields.Many2many('account.payment', string='Payment Details')

    @api.model
    def default_get(self, fields_list):
        res = super(CustomerStatementWizard, self).default_get(fields_list)
        partner_id = self.env.context.get('default_partner_id') or self.env.context.get('active_id')
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            res.update({
                'partner_id': partner.id,
                'sale_order_ids': [(6, 0, self.env['sale.order'].search([
                    ('partner_id', 'child_of', partner.commercial_partner_id.id),
                    ('state', 'in', ['sale', 'done'])
                ]).ids)],
                'payment_ids': [(6, 0, self.env['account.payment'].search([
                    ('partner_id', 'child_of', partner.commercial_partner_id.id),
                    ('state', 'not in', ['draft', 'cancel']),
                    ('payment_type', '=', 'inbound')
                ]).ids)],
            })
        return res

    def action_print(self):
        return self.partner_id.action_generate_statement_report()
