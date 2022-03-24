from apps.mappings.tasks import schedule_cost_centers_creation, schedule_fyle_attributes_creation, schedule_projects_creation


class ImportSettingsTrigger:
    """
    All the post save actions of Import Saettings API
    """
    def __init__(self, workspace_general_settings, mapping_settings, workspace_id):
        self.__workspace_general_settings = workspace_general_settings
        self.__mapping_settings = mapping_settings
        self.__workspace_id = workspace_id
    
    def post_save_workspace_general_settings(self):
        """
        Post save action for workspace general settings
        """
        pass

    def pre_save_mapping_settings(self):
        """
        Post save action for mapping settings
        """
        mapping_settings = self.__mapping_settings

        projects_mapping_available = False
        cost_center_mapping_available = False
        custom_field_mapping_available = False

        for setting in mapping_settings:
            if setting['source_field'] == 'PROJECT':
                projects_mapping_available = True
            elif setting['source_field'] == 'COST_CENTER':
                cost_center_mapping_available = True
            elif setting['source_field'] == 'CUSTOM_FIELD':
                custom_field_mapping_available = True
        
        if not projects_mapping_available:
            schedule_projects_creation(False, self.__workspace_id)
        
        if not cost_center_mapping_available:
            schedule_cost_centers_creation(False, self.__workspace_id)
        
        if not custom_field_mapping_available:
            schedule_fyle_attributes_creation(self.__workspace_id)
