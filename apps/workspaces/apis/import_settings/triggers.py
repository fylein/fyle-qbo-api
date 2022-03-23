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

    def post_save_mapping_settings(self):
        """
        Post save action for mapping settings
        """
        pass
