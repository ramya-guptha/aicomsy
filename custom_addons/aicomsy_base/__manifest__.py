# -*- coding: utf-8 -*-
{
    'name': 'Aicomsy Base',
    'depends': [
        'base', 'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/x_location_views.xml',
        'data/x_location_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'aicomsy_base/static/src/*',
            'aicomsy_base/static/src/scss/custom_style.scss',
            'aicomsy_base/static/src/css/dashboard.css',
            'web/static/lib/Chart/Chart.js'

        ],

    },
    'installable': True,
    'license': 'LGPL-3',
}
