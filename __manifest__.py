{
    'name': 'Planning Preventive Maintenance',
    'version': '1.8',
    'summary': 'Planning Preventive Maintenance',
    'depends': [
        'base',
        'mail',
        'maintenance',  # main app
        'mrp',  # from conf (Work Orders) to work of #(work center)#
        'mrp_maintenance',  # work center
    ],
    'data': [
        'security/ir.model.access.csv',
        # ##################################################
        'data/maintenance_request_data.xml',
        # ##################################################

        'wizard/validate_spare_part_wizard_views.xml',
        'wizard/planned_preventive_wizard_views.xml',
        'wizard/equipment_readings_wizard_views.xml',
        # ##################################################

        'views/maintenance_equipment_views.xml',
        'views/maintenance_request_views.xml',
        'views/product_template_view.xml',
        'views/menuitem_views.xml',

    ],

    'sequence': 1,
    'application': True,
    'license': 'LGPL-3',

}
