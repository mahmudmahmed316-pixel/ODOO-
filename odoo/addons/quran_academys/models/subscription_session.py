from odoo import models, fields

class AcademySubscriptionSession(models.Model):
    _name = 'academy.subscription.session'
    _description = 'Scheduled Session for Subscription'
    _order = 'session_date'

    subscription_id = fields.Many2one(
        'academy.subscription',
        string='Subscription',
        required=True,
        ondelete='cascade',
    )
    session_date = fields.Datetime(
        string='Session Date & Time',
        required=True,
    )
    topic = fields.Char(
        string='Topic / Chapter',
    )
    meeting_link = fields.Char(
        string='Meeting Link',
        help='Zoom or Google Meet link',
    )
    notes = fields.Text(string='Notes')
