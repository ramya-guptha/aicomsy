# -*- coding: utf-8 -*-


{
    'name': 'Incident Management',
    'depends': [
        'base', 'hr', 'maintenance',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/incident_record_views.xml',
        'views/incident_management_menu.xml',
        'views/inc_person_views.xml',
        'views/inc_asset_views.xml',
        'views/inc_spills_views.xml',
        'views/inc_mva_views.xml',
        'data/mail_template_data.xml',
        'data/incident_type_data.xml',
        'data/incident_person_category_data.xml',
        'data/incident_injury_type_data.xml',
        'data/incident_injured_body_parts_data.xml',
        'data/incident_person_immediate_response_data.xml',
        'data/incident_asset_immediate_response_data.xml',
        'data/x_inc_spill_immediate_response_data.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
