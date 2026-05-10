{
    'name': 'Partner Account Statement',
    'version': '18.0.1.4.0',
    'category': 'Accounting',
    'summary': 'Professional accounting-accurate partner account statement (Invoices, Payments, Balance)',
    'author': 'Senior Odoo Developer',
    'depends': ['account'],
    'data': [
        'views/res_partner_view.xml',
        'views/report_invoice_inherit.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
