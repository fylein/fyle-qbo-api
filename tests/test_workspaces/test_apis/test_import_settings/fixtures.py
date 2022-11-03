data = {
    'import_settings': {
        'workspace_general_settings': {
            'import_categories': True,
            'charts_of_accounts': [
                'Expense'
            ],
            'import_tax_codes': True,
            'import_vendors_as_merchants': True
        },
        'general_mappings': {
            'default_tax_code': {
                'name': '12.5% TR @12.5%',
                'id': '22'
            }
        },
        'mapping_settings': [
            {
                'source_field': 'COST_CENTER',
                'destination_field': 'DEPARTMENT',
                'import_to_fyle': True,
                'is_custom': False,
                'source_placeholder': 'cost center'
            },
            {
                'source_field': 'PROJECT',
                'destination_field': 'CLASS',
                'import_to_fyle': True,
                'is_custom': False,
                'source_placeholder': 'project'
            },
            {
                'source_field': 'CLASS',
                'destination_field': 'CUSTOMER',
                'import_to_fyle': True,
                'is_custom': True,
                'source_placeholder': 'class'
            }
        ]
    },
    'import_settings_without_mapping': {
        'workspace_general_settings': {
            'import_categories': True,
            'charts_of_accounts': [
                'Expense'
            ],
            'import_tax_codes': True,
            'import_vendors_as_merchants': True
        },
        'general_mappings': {
            'default_tax_code': {
                'name': '12.5% TR @12.5%',
                'id': '22'
            }
        },
        'mapping_settings': [
            {
                'source_field': 'CLASS',
                'destination_field': 'CUSTOMER',
                'import_to_fyle': True,
                'is_custom': True,
                'source_placeholder': 'class'
            }
        ]
    },
    'response': {'workspace_general_settings':{'import_categories':True,'charts_of_accounts':['Expense'],'import_tax_codes':True,'import_vendors_as_merchants':True},'general_mappings':{'default_tax_code':{'name':'12.5% TR @12.5%','id':'22'}},'mapping_settings':[{'source_field':'COST_CENTER','destination_field':'CLASS','import_to_fyle':True,'is_custom':False,'source_placeholder':''},{'source_field':'PROJECT','destination_field':'DEPARTMENT','import_to_fyle':True,'is_custom':False,'source_placeholder':''},{'source_field':'CLASS','destination_field':'CUSTOMER','import_to_fyle':True,'is_custom':True,'source_placeholder':''}],
        'workspace_id':9
    },
    'import_settings_missing_values': {
        'mapping_settings': None,
        'workspace_general_settings': {},
        'general_mappings': {}
    },

}