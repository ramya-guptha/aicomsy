# -*- coding: utf-8 -*-

{
    'name': 'Legal Register',
    'category': 'Aicomsy/Aicomsy',
    'depends': ['base', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/x_legal_register_views.xml',
        'views/x_legal_regulation_views.xml',
        'views/x_monitoring_measurement_views.xml',
        'views/legal_register_menu.xml',
        'data/x_legal_classification_data.xml',
        'data/x_legal_env_data.xml',
        'data/x_legal_saso_data.xml',
        'data/x_legal_mhrs_data.xml',

    ],

    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
