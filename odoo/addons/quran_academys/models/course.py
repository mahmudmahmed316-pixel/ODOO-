from odoo import models, fields

class AcademyCourse(models.Model):
    _name = 'academy.course'
    _description = 'Academy Course'

    name = fields.Char(string='Course Name', required=True)
    teacher_id = fields.Many2one(
        'res.users',
        string='Teacher',
        domain=lambda self: [('groups_id', 'in', self.env.ref('quran_academys.group_academy_teacher').id)],
        required=True
    )
    student_ids = fields.Many2many(
        'academy.student',
        string='Enrolled Students'
    )
    session_ids = fields.One2many(
        'academy.session',
        'course_id',
        string='Sessions'
    )
