from odoo import models, fields

class AcademyHomework(models.Model):
    _name = 'academy.homework'
    _description = 'Academy Homework'
    _order = 'create_date desc'

    student_id = fields.Many2one('academy.student', string='Student', required=True)
    session_id = fields.Many2one('academy.session', string='Session')
    course_id = fields.Many2one('academy.course', string='Course', related='session_id.course_id', store=True)
    
    file = fields.Binary(string='Homework File', attachment=True, required=True)
    filename = fields.Char(string='File Name')
    
    state = fields.Selection([
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed')
    ], string='Status', default='submitted', required=True)
    
    teacher_notes = fields.Text(string='Teacher Notes')

    def action_reviewed(self):
        for rec in self:
            rec.state = 'reviewed'
            # Automatically update the session line homework status
            if rec.session_id and rec.student_id:
                session_line = self.env['academy.session.line'].search([
                    ('session_id', '=', rec.session_id.id),
                    ('student_id', '=', rec.student_id.id)
                ], limit=1)
                if session_line:
                    session_line.homework_done = True

