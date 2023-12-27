{
    'name': 'Non conformance Management',
    'category': 'Aicomsy/Aicomsy',
    'depends': [
        'base', 'aicomsy_base', 'hr', 'account', 'mail'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/x_ncr_report_views.xml',
        'views/x_ncr_nc_views.xml',
        'views/x_ncr_report_lov_views.xml',
        'views/x_ncr_response_views.xml',
        'views/x_ncr_menu.xml',
        'views/dashboard_views.xml',
        'report/report.xml',
        'report/ncr_report.xml',
        'data/x_ncr_type_data.xml',
        'data/x_ncr_discipline_data.xml',
        'data/x_ncr_source_data.xml',
        'data/x_ncr_category_data.xml',
        'data/mail_template_data.xml',
        'data/x_ncr_disposition_type_data.xml',
        'data/x_ncr_ca_response_data.xml',
        'data/x_ncr_cause_of_nc_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'non_conformance_report/static/src/js/dashboard.js',
            'non_conformance_report/static/src/xml/dashboard.xml',
        ],
    },

    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
