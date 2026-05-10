from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Customer Accounting (Receivable)
    customer_total_invoices = fields.Monetary(
        string='Total Sales Invoices',
        compute='_compute_partner_accounting_totals',
        currency_field='currency_id'
    )
    customer_total_payments = fields.Monetary(
        string='Total Customer Payments',
        compute='_compute_partner_accounting_totals',
        currency_field='currency_id'
    )
    customer_balance = fields.Monetary(
        string='Customer Net Balance',
        compute='_compute_partner_accounting_totals',
        currency_field='currency_id'
    )

    # Vendor Accounting (Payable)
    vendor_total_bills = fields.Monetary(
        string='Total Vendor Bills',
        compute='_compute_partner_accounting_totals',
        currency_field='currency_id'
    )
    vendor_total_payments = fields.Monetary(
        string='Total Vendor Payments',
        compute='_compute_partner_accounting_totals',
        currency_field='currency_id'
    )
    vendor_balance = fields.Monetary(
        string='Vendor Net Balance',
        compute='_compute_partner_accounting_totals',
        currency_field='currency_id'
    )

    # Overall Totals
    total_debit = fields.Monetary(
        string='Total Debit',
        compute='_compute_partner_accounting_totals',
        currency_field='currency_id'
    )
    total_credit = fields.Monetary(
        string='Total Credit',
        compute='_compute_partner_accounting_totals',
        currency_field='currency_id'
    )
    final_balance = fields.Monetary(
        string='Final Balance',
        compute='_compute_partner_accounting_totals',
        currency_field='currency_id'
    )

    def _compute_partner_accounting_totals(self):
        for partner in self:
            domain = [
                ('partner_id', '=', partner.id),
                ('move_id.state', 'in', ('draft', 'posted')),
                ('account_id.account_type', 'in', ('asset_receivable', 'liability_payable'))
            ]
            
            move_lines = self.env['account.move.line'].sudo().search(domain)
            
            c_invoices = 0.0
            c_payments = 0.0
            v_bills = 0.0
            v_payments = 0.0
            t_debit = 0.0
            t_credit = 0.0
            
            for line in move_lines:
                t_debit += line.debit
                t_credit += line.credit
                
                if line.account_id.account_type == 'asset_receivable':
                    # Customer logic: Debit = Invoice, Credit = Payment
                    c_invoices += line.debit
                    c_payments += line.credit
                elif line.account_id.account_type == 'liability_payable':
                    # Vendor logic: Credit = Bill, Debit = Payment
                    v_bills += line.credit
                    v_payments += line.debit
            
            partner.customer_total_invoices = c_invoices
            partner.customer_total_payments = c_payments
            partner.customer_balance = c_invoices - c_payments
            
            partner.vendor_total_bills = v_bills
            partner.vendor_total_payments = v_payments
            partner.vendor_balance = v_bills - v_payments
            
            partner.total_debit = t_debit
            partner.total_credit = t_credit
            partner.final_balance = t_debit - t_credit

    # Action methods for drill-down
    def _create_move_line_action(self, name, domain):
        return {
            'name': name,
            'view_mode': 'list,form',
            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
            'domain': domain,
            'context': {'search_default_group_by_move': 1, 'expand': 1},
            'target': 'current',
        }

    def action_view_customer_invoices_details(self):
        domain = [
            ('partner_id', '=', self.id),
            ('move_id.state', 'in', ('draft', 'posted')),
            ('account_id.account_type', '=', 'asset_receivable'),
            ('debit', '>', 0)
        ]
        return self._create_move_line_action(_('Customer Invoices Details'), domain)

    def action_view_customer_payments_details(self):
        domain = [
            ('partner_id', '=', self.id),
            ('move_id.state', 'in', ('draft', 'posted')),
            ('account_id.account_type', '=', 'asset_receivable'),
            ('credit', '>', 0)
        ]
        return self._create_move_line_action(_('Customer Payments Details'), domain)

    def action_view_vendor_bills_details(self):
        domain = [
            ('partner_id', '=', self.id),
            ('move_id.state', 'in', ('draft', 'posted')),
            ('account_id.account_type', '=', 'liability_payable'),
            ('credit', '>', 0)
        ]
        return self._create_move_line_action(_('Vendor Bills Details'), domain)

    def action_view_vendor_payments_details(self):
        domain = [
            ('partner_id', '=', self.id),
            ('move_id.state', 'in', ('draft', 'posted')),
            ('account_id.account_type', '=', 'liability_payable'),
            ('debit', '>', 0)
        ]
        return self._create_move_line_action(_('Vendor Payments Details'), domain)

class AccountMove(models.Model):
    _inherit = 'account.move'

    partner_previous_balance = fields.Monetary(
        string='Previous Balance',
        compute='_compute_partner_report_balances'
    )
    partner_total_due = fields.Monetary(
        string='Total Due',
        compute='_compute_partner_report_balances'
    )

    def _compute_partner_report_balances(self):
        for move in self:
            if not move.partner_id:
                move.partner_previous_balance = 0.0
                move.partner_total_due = 0.0
                continue

            # Calculate current partner balance (all posted/draft moves)
            # This is effectively the "Final Balance" after this invoice
            current_balance = move.partner_id.final_balance
            
            # Previous balance = Final Balance - Current Invoice Balance Effect
            # For Customer (Out Invoice): Balance increases by debit (amount_total)
            # For Vendor (In Bill): Balance decreases by credit (amount_total)
            
            invoice_effect = 0.0
            if move.move_type in ('out_invoice', 'out_refund'):
                # Effect on receivable (debit - credit)
                invoice_effect = move.amount_total if move.move_type == 'out_invoice' else -move.amount_total
            elif move.move_type in ('in_invoice', 'in_refund'):
                # Effect on payable (debit - credit)
                # Note: final_balance is (Debit - Credit). 
                # An In Invoice increases Credit, so it decreases (Debit - Credit).
                invoice_effect = -move.amount_total if move.move_type == 'in_invoice' else move.amount_total

            move.partner_previous_balance = current_balance - invoice_effect
            move.partner_total_due = current_balance
