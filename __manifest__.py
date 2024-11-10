{
    'name':'project_enhancement',
    'author':'Moustafa Khalil',
    'depends':['base','hr','project'],
    'data':[

        'security/ir.model.access.csv',
        'views/project_collaborator.xml',
        'views/hr_employee.xml',
        'views/project_project_views.xml',
        'views/project_task.xml',
        'data/project_task_number.xml',
        'reports/project_report_template.xml',
        # 'views/project_report.xml',

    ],

    'assets': {
        'web.report_assets_common': [
            'project_enhancement/static/src/css/project_report.css',
        ],
    }

}