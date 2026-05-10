from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
import base64
import werkzeug

class AcademyPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        student = request.env['academy.student'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        if student:
            session_count = request.env['academy.session.line'].sudo().search_count([('student_id', '=', student.id)])
            values['session_count'] = session_count
            
            homework_count = request.env['academy.homework'].sudo().search_count([('student_id', '=', student.id)])
            values['homework_count'] = homework_count
        return values

    @http.route(['/my/dashboard'], type='http', auth='user', website=True)
    def portal_academy_dashboard(self, **kw):
        values = self._prepare_portal_layout_values()
        
        partner_id = request.env.user.partner_id.id
        students = request.env['academy.student'].sudo().search([
            '|', 
            ('user_id', '=', request.env.user.id),
            ('parent_id', '=', partner_id)
        ])
        
        selected_student_id = int(kw.get('student_id', 0))
        if selected_student_id:
            student = students.filtered(lambda s: s.id == selected_student_id)
            if not student:
                student = students[0] if students else request.env['academy.student'].sudo()
        else:
            student = students[0] if students else request.env['academy.student'].sudo()
            
        if not student:
            values.update({
                'student': request.env['academy.student'].sudo(),
                'evaluations': [],
                'attendance_rate': 0,
                'upcoming_sessions': [],
                'page_name': 'academy_dashboard',
                'warning': 'Your account is not linked to any student profile. Please contact the administration.'
            })
            return request.render('quran_academys.portal_academy_dashboard', values)

        evaluations = request.env['academy.session.line'].sudo().search([('student_id', '=', student.id)], order='create_date desc', limit=5)
        
        # Calculate attendance rate
        total_sessions = request.env['academy.session.line'].sudo().search_count([('student_id', '=', student.id)])
        attended_sessions = request.env['academy.session.line'].sudo().search_count([('student_id', '=', student.id), ('attendance', '=', 'present')])
        
        attendance_rate = 0
        if total_sessions > 0:
            attendance_rate = round((attended_sessions / total_sessions) * 100)

        upcoming_sessions = request.env['academy.session'].sudo().search([
            ('id', 'in', student.course_ids.mapped('session_ids').ids),
            ('state', '=', 'draft')
        ], order='date asc', limit=5)

        values.update({
            'student': student,
            'students': students,
            'evaluations': evaluations,
            'attendance_rate': attendance_rate,
            'upcoming_sessions': upcoming_sessions,
            'page_name': 'academy_dashboard'
        })
        return request.render('quran_academys.portal_academy_dashboard', values)

    @http.route(['/my/sessions', '/my/sessions/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_sessions(self, page=1, **kw):
        partner_id = request.env.user.partner_id.id
        students = request.env['academy.student'].sudo().search([
            '|', 
            ('user_id', '=', request.env.user.id),
            ('parent_id', '=', partner_id)
        ])
        
        selected_student_id = int(kw.get('student_id', 0))
        if selected_student_id:
            student = students.filtered(lambda s: s.id == selected_student_id)
            if not student:
                student = students[0] if students else request.env['academy.student'].sudo()
        else:
            student = students[0] if students else request.env['academy.student'].sudo()
            
        if not student:
            return request.redirect('/my/dashboard')

        domain = [('student_id', '=', student.id)]
        session_count = request.env['academy.session.line'].sudo().search_count(domain)
        
        pager = portal_pager(
            url="/my/sessions",
            total=session_count,
            page=page,
            step=10
        )
        
        evaluations = request.env['academy.session.line'].sudo().search(
            domain, order='create_date desc', limit=10, offset=pager['offset']
        )

        values = self._prepare_portal_layout_values()
        values.update({
            'student': student,
            'students': students,
            'evaluations': evaluations,
            'pager': pager,
            'page_name': 'academy_sessions'
        })
        return request.render('quran_academys.portal_my_sessions', values)

    @http.route(['/my/homework'], type='http', auth='user', website=True)
    def portal_my_homework(self, **post):
        partner_id = request.env.user.partner_id.id
        students = request.env['academy.student'].sudo().search([
            '|', 
            ('user_id', '=', request.env.user.id),
            ('parent_id', '=', partner_id)
        ])
        
        selected_student_id = int(post.get('student_id', 0))
        if selected_student_id:
            student = students.filtered(lambda s: s.id == selected_student_id)
            if not student:
                student = students[0] if students else request.env['academy.student'].sudo()
        else:
            student = students[0] if students else request.env['academy.student'].sudo()
            
        if not student:
            return request.redirect('/my/dashboard')

        if request.httprequest.method == 'POST' and post.get('file'):
            file = post.get('file')
            session_id = int(post.get('session_id')) if post.get('session_id') else False
            
            request.env['academy.homework'].sudo().create({
                'student_id': student.id,
                'session_id': session_id,
                'filename': file.filename,
                'file': base64.b64encode(file.read()),
                'state': 'submitted'
            })
            return request.redirect('/my/homework')

        homeworks = request.env['academy.homework'].sudo().search([('student_id', '=', student.id)], order='create_date desc')
        available_sessions = request.env['academy.session'].sudo().search([('id', 'in', student.course_ids.mapped('session_ids').ids)])

        values = self._prepare_portal_layout_values()
        values.update({
            'student': student,
            'students': students,
            'homeworks': homeworks,
            'available_sessions': available_sessions,
            'page_name': 'academy_homework'
        })
        return request.render('quran_academys.portal_my_homework', values)
