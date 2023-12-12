# -*- coding: utf-8 -*-
{
    'name': 'Aicomsy Base',
    'depends': [
        'base','hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            'aicomsy_base/static/src/*',
        ],

    },
    'installable': True,
    'license': 'LGPL-3',
}
