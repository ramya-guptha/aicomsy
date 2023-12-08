{
    'name': 'Non conformance Report',

    'depends': [
        'base', 'aicomsy_base','hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/x_ncr_report_views.xml',
        'views/x_ncr_nc_views.xml',
        'views/x_ncr_report_lov_views.xml',
        'views/x_ncr_menu.xml',
        'views/x_ncr_response_views.xml',
        'data/x_ncr_type_data.xml',
        'data/x_ncr_discipline_data.xml',
        'data/x_ncr_source_data.xml',
        'data/x_ncr_category_data.xml',
    ],

    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
