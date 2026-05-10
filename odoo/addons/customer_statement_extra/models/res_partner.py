from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_sales_count = fields.Integer(
        string='Number of Sales',
        compute='_compute_customer_sales_count',
        help='Total number of validated sales orders for this customer.'
    )
    
    customer_total_sales_amount = fields.Monetary(
        string='Total Sales Amount',
        compute='_compute_customer_sales_count', # Computed in the same method
        currency_field='currency_id'
    )

    total_payments_amount = fields.Monetary(
        string='Total Payments',
        compute='_compute_total_payments_amount',
        currency_field='currency_id',
        help='Total sum of payments made by this customer (posted).'
    )

    customer_balance = fields.Monetary(
        string='Remaining Balance',
        compute='_compute_customer_balance',
        currency_field='currency_id'
    )

    def _compute_customer_sales_count(self):
        for partner in self:
            # Count and Sum sale orders that are in 'sale' or 'done' state
            sales = self.env['sale.order'].search([
                ('partner_id', 'child_of', partner.commercial_partner_id.id),
                ('state', 'in', ['sale', 'done'])
            ])
            partner.customer_sales_count = len(sales)
            partner.customer_total_sales_amount = sum(sales.mapped('amount_total'))

    def _compute_total_payments_amount(self):
        for partner in self:
            # Sum account payments that are not draft or cancelled
            payments = self.env['account.payment'].search([
                ('partner_id', 'child_of', partner.commercial_partner_id.id),
                ('state', 'not in', ['draft', 'cancel']),
                ('payment_type', '=', 'inbound')
            ])
            partner.total_payments_amount = sum(payments.mapped('amount'))

    @api.depends('customer_total_sales_amount', 'total_payments_amount')
    def _compute_customer_balance(self):
        for partner in self:
            partner.customer_balance = partner.customer_total_sales_amount - partner.total_payments_amount

    def action_print_customer_statement(self):
        """ Action to open the wizard """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer Statement Summary',
            'res_model': 'customer.statement.wizard',
            'view_mode': 'form',
            'target': 'main',
            'context': {'default_partner_id': self.id},
        }

    def action_generate_statement_report(self):
        """ Actual logic to trigger the QWeb PDF report """
        return self.env.ref('customer_statement_extra.action_report_customer_statement').report_action(self)
