from odoo import models, fields, api

class AcademySubscription(models.Model):
    _name = 'academy.subscription'
    _description = 'Student Subscription'
    _order = 'start_date desc'

    name = fields.Char(string='Subscription Name', required=True, default='Monthly Plan')
    student_id = fields.Many2one('academy.student', string='Student', required=True)
    start_date = fields.Date(string='Start Date', required=True, default=fields.Date.context_today)
    end_date = fields.Date(string='End Date', required=True)
    
    allowed_sessions = fields.Integer(string='Allowed Sessions', required=True, default=8)
    attended_sessions = fields.Integer(string='Attended Sessions', compute='_compute_sessions', store=True)
    remaining_sessions = fields.Integer(string='Remaining Sessions', compute='_compute_sessions', store=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True)

    session_line_ids = fields.One2many('academy.session.line', 'subscription_id', string='Attended Sessions')
    session_schedule_ids = fields.One2many('academy.subscription.session', 'subscription_id', string='Scheduled Sessions')
    
    price = fields.Monetary(string='Price', required=True, default=0.0)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True)
    payment_state = fields.Selection(related='invoice_id.payment_state', string='Payment Status')

    @api.depends('session_line_ids', 'allowed_sessions')
    def _compute_sessions(self):
        for sub in self:
            consumed = len(sub.session_line_ids)
            sub.attended_sessions = consumed
            sub.remaining_sessions = sub.allowed_sessions - consumed
    def action_active(self):
        self.write({'state': 'active'})

    def action_expire(self):
        self.write({'state': 'expired'})
        
    def action_cancel(self):
        self.write({'state': 'cancelled'})
        
    def action_create_invoice(self):
        for sub in self:
            if sub.invoice_id:
                continue
            invoice_vals = {
                'move_type': 'out_invoice',
                'partner_id': sub.student_id.parent_id.id or sub.student_id.partner_id.id,
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': [(0, 0, {
                    'name': f"Subscription: {sub.name}",
                    'quantity': 1,
                    'price_unit': sub.price,
                })]
            }
            invoice = self.env['account.move'].create(invoice_vals)
            sub.invoice_id = invoice.id
        return True
