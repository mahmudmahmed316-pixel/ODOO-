from odoo import models, fields, api

class AcademyStudent(models.Model):
    _name = 'academy.student'
    _description = 'Academy Student'
    _inherits = {'res.partner': 'partner_id'}

    _sql_constraints = [
        ('user_unique', 'unique(user_id)', 'This portal user is already assigned to another student!'),
    ]


    
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
        ondelete='cascade'
    )
    user_id = fields.Many2one(
        'res.users',
        string='Portal User',
        help='Linked portal user for website access.'
    )
    parent_id = fields.Many2one(
        'res.partner',
        string='Parent / Guardian',
        help='Parent who manages this student and pays subscriptions.'
    )
    course_ids = fields.Many2many(
        'academy.course',
        string='Courses'
    )
    homework_ids = fields.One2many(
        'academy.homework',
        'student_id',
        string='Homeworks'
    )
    session_line_ids = fields.One2many(
        'academy.session.line',
        'student_id',
        string='Session Evaluations'
    )
    subscription_ids = fields.One2many(
        'academy.subscription',
        'student_id',
        string='Subscriptions'
    )
    active_subscription_id = fields.Many2one(
        'academy.subscription',
        string='Active Subscription',
        compute='_compute_active_subscription'
    )
    has_active_subscription = fields.Boolean(
        string='Has Active Subscription',
        compute='_compute_has_active_subscription',
        store=True
    )

    @api.depends('active_subscription_id')
    def _compute_has_active_subscription(self):
        for rec in self:
            rec.has_active_subscription = bool(rec.active_subscription_id)

    remaining_sessions = fields.Integer(
        string='Remaining Sessions',
        related='active_subscription_id.remaining_sessions',
        readonly=True
    )
    schedule_ids = fields.One2many(
        'academy.student.schedule',
        'student_id',
        string='Schedule'
    )
    
    session_count = fields.Integer(string='Sessions', compute='_compute_counts')
    subscription_count = fields.Integer(string='Subscriptions', compute='_compute_counts')

    def _compute_counts(self):
        for student in self:
            student.session_count = len(student.session_line_ids)
            student.subscription_count = len(student.subscription_ids)

    def _compute_active_subscription(self):
        for student in self:
            active_sub = self.env['academy.subscription'].search([
                ('student_id', '=', student.id),
                ('state', '=', 'active')
            ], order='start_date desc', limit=1)
            student.active_subscription_id = active_sub.id if active_sub else False

class AcademyStudentSchedule(models.Model):
    _name = 'academy.student.schedule'
    _description = 'Student Schedule'
    _order = 'day_of_week, time_from'

    student_id = fields.Many2one('academy.student', string='Student', required=True, ondelete='cascade')
    day_of_week = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
    ], string='Day of Week', required=True)
    
    time_from = fields.Float(string='From Time', required=True)
    time_to = fields.Float(string='To Time', required=True)
    
    teacher_id = fields.Many2one('res.users', string='Teacher')
