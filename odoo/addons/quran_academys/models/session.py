from odoo import models, fields, api, _

class AcademySession(models.Model):
    _name = 'academy.session'
    _description = 'Academy Session'
    _order = 'date desc'

    name = fields.Char(string='Session Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    course_id = fields.Many2one('academy.course', string='Course', required=True)
    teacher_id = fields.Many2one('res.users', related='course_id.teacher_id', string='Teacher', store=True, readonly=True)
    date = fields.Datetime(string='Date & Time', required=True, default=fields.Datetime.now)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)
    
    meeting_link = fields.Char(string='Virtual Meeting Link', help="Zoom or Google Meet Link")
    topic = fields.Char(string='Topic / Chapter', help="What was covered in this session?")
    reminder_sent = fields.Boolean(string='Reminder Sent', default=False)
    
    line_ids = fields.One2many('academy.session.line', 'session_id', string='Students Evaluations')

    @api.model
    def cron_send_session_reminders(self):
        # Find sessions starting in the next 20 minutes that haven't been notified yet
        now = fields.Datetime.now()
        soon = fields.Datetime.add(now, minutes=20)
        
        sessions = self.search([
            ('date', '>=', now),
            ('date', '<=', soon),
            ('reminder_sent', '=', False),
            ('state', '=', 'draft')
        ])
        
        template = self.env.ref('quran_academys.email_template_session_reminder', raise_if_not_found=False)
        if not template:
            return
            
        for session in sessions:
            # Send to all students in the session
            session.message_post_with_source(
                template,
                subtype_xmlid='mail.mt_comment',
            )
            session.reminder_sent = True


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('academy.session') or _('New')
        return super().create(vals_list)

    @api.onchange('course_id')
    def _onchange_course_id(self):
        if self.course_id:
            # Auto-populate students from the course
            lines = [(5, 0, 0)]
            for student in self.course_id.student_ids:
                lines.append((0, 0, {
                    'student_id': student.id,
                }))
            self.line_ids = lines

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_draft(self):
        self.write({'state': 'draft'})


class AcademySessionLine(models.Model):
    _name = 'academy.session.line'
    _description = 'Academy Session Evaluation Line'

    session_id = fields.Many2one('academy.session', string='Session', required=True, ondelete='cascade')
    student_id = fields.Many2one('academy.student', string='Student', required=True)
    
    attendance = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent')
    ], string='Attendance', default='present', required=True)
    
    subscription_id = fields.Many2one('academy.subscription', string='Subscription', domain="[('student_id', '=', student_id)]")
    
    homework_done = fields.Boolean(string='Homework Done')
    
    recitation_level = fields.Selection([
        ('excellent', 'Excellent'),
        ('very_good', 'Very Good'),
        ('good', 'Good'),
        ('weak', 'Weak')
    ], string='Recitation Level')
    
    memorization = fields.Selection([
        ('perfect', 'Perfect'),
        ('revision', 'Needs Revision'),
        ('mistake', 'Has Mistakes')
    ], string='Memorization')
    
    session_rating = fields.Selection([
        ('very_good', 'Very Good'),
        ('good', 'Good'),
        ('accepted', 'Accepted'),
        ('weak', 'Weak')
    ], string='Overall Rating')
    
    notes = fields.Text(string='Teacher Notes')
    next_homework = fields.Text(string='Homework for Next Session')

    status_color = fields.Selection([
        ('blue', 'Blue (Excellent)'),
        ('green', 'Green (Good)'),
        ('yellow', 'Yellow (Warning)'),
        ('red', 'Red (Danger)'),
        ('gray', 'Gray (Absent)')
    ], string='Status Color', compute='_compute_status_color', store=True)

    @api.onchange('student_id', 'attendance')
    def _onchange_student_subscription(self):
        if self.student_id and self.attendance == 'present' and not self.subscription_id:
            if self.student_id.active_subscription_id:
                self.subscription_id = self.student_id.active_subscription_id

    @api.depends('attendance', 'homework_done', 'recitation_level', 'memorization')
    def _compute_status_color(self):
        for record in self:
            if record.attendance == 'absent':
                record.status_color = 'gray'
            elif record.recitation_level == 'excellent' and record.memorization == 'perfect' and record.homework_done:
                record.status_color = 'blue'
            elif record.recitation_level in ['excellent', 'very_good'] and record.memorization in ['perfect', 'revision'] and record.homework_done:
                record.status_color = 'green'
            elif not record.homework_done and record.recitation_level in ['excellent', 'very_good', 'good']:
                record.status_color = 'yellow'
            else:
                record.status_color = 'red'

    def action_mark_absent(self):
        for record in self:
            record.attendance = 'absent'
        return True

    def action_mark_present(self):
        for record in self:
            record.attendance = 'present'
        return True
