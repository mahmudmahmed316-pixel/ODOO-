{
    'name': 'Premium Home Menu (Enterprise Style)',
    'version': '18.0.1.0.3',
    'category': 'Themes/Backend',
    'summary': 'Professional Grid Menu for Odoo 18 Community',
    'author': 'Senior Odoo Developer',
    'depends': ['web'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'community_premium_menu/static/src/scss/home_menu.scss',
            'community_premium_menu/static/src/xml/home_menu.xml',
            'community_premium_menu/static/src/js/home_menu.js',
        ],
    },
    'installable': True,
    'license': 'LGPL-3',
}
