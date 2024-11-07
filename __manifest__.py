{
    'name': 'UNIACME',
    'version': '1.0',
    'category': 'Human Resources',
    'sequence': 200,
    'summary': 'Voting system for UNIACME',
    'description': """
                        This module manages voting workflow
                    """,
    'depends': ['web', 'base_setup', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/campus_views.xml',
        'views/voting_process.xml',
        'views/voting_process_templates.xml',
        'wizard/voting_process_importer_wizard_views.xml',
        'views/menu_views.xml',
    ],
    'application': True,
    'installable': True,
    'assets': {
        'web.assets_backend': [
            'uniacme_votes/static/src/**',
        ],
    },
    'license': 'GPL-3',
}
