{
    'name': 'Customer Statement Extra',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Enhanced Customer Statement with sales count and total payments.',
    'description': """
        This module adds custom fields and a report for customer statements:
        - Total Number of Sales.
        - Total Payments (linked to invoices or standalone).
        - Printable QWeb Report.
    """,
    'author': 'Antigravity',
    'depends': ['base', 'sale', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'reports/report_actions.xml',
        'reports/customer_statement_template.xml',
        'wizard/customer_statement_wizard_view.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
