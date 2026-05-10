{
    'name': 'Community Studio Lite',
    'version': '18.0.1.0.0',
    'category': 'Tools',
    'summary': 'Add custom fields and customize views dynamically (Developer Tool)',
    'author': 'Senior Odoo Developer',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/studio_field_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
