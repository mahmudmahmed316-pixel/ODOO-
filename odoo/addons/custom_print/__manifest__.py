{
    'name': 'Custom Commercial Print & Design',
    'version': '18.0.1.0.1',
    'category': 'Sales/Sales',
    'summary': 'Custom Commercial Invoice layout and bilingual form actions for SO/PO',
    'author': 'Senior Odoo Developer',
    'depends': ['sale', 'purchase', 'account'],
    'data': [
        'views/report_commercial_template.xml',
        'report/commercial_report_action.xml',
        'views/sale_order_view_inherit.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
