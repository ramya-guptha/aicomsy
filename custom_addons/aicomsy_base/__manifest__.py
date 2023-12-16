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
        ],

    },
    'installable': True,
    'license': 'LGPL-3',
}
