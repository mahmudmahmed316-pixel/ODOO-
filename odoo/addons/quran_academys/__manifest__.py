{
    'name': 'Quran Academy Management',
    'version': '1.0',
    'category': 'Education',
    'summary': 'Student Management System for Quran Memorization Academy',
    'description': """
        Manage students, courses, sessions, attendance, homework, and evaluations.
        Provides a web portal for students to view their progress and upload homework.
    """,
    'author': 'Your Company',
    'depends': ['base', 'mail', 'portal', 'account', 'calendar'],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'data/mail_templates.xml',
        'data/cron.xml',
        'data/sequence_data.xml',
        'views/menu_views.xml',
        'views/subscription_views.xml',
        'views/session_views.xml',
        'views/student_views.xml',
        'views/course_views.xml',
        'views/homework_views.xml',
        'views/portal_templates.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
