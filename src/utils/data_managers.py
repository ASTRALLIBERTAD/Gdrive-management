from pathlib import Path
import json


class BaseDataManager:
    def __init__(self, data_dir, file_name):
        self.data_dir = Path(data_dir) if isinstance(data_dir, str) else data_dir
        self.data_dir.mkdir(exist_ok=True)
        self.file_path = self.data_dir / file_name
    
    def load(self, default=None):
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {self.file_path}: {e}")
        return default if default is not None else []
    
    def save(self, data):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving {self.file_path}: {e}")
            return False


class SyncedDataManager(BaseDataManager):
    def __init__(self, data_dir, file_name, drive_service=None, drive_parent_id=None):
        super().__init__(data_dir, file_name)
        self.drive_service = drive_service
        self.drive_parent_id = drive_parent_id
    
    def load(self, default=None):
        if self.drive_service and self.drive_parent_id:
            try:
                file = self.drive_service.find_file(self.file_path.name, self.drive_parent_id)
                if file:
                    content = self.drive_service.read_file_content(file['id'])
                    if content:
                        return json.loads(content)
            except Exception as e:
                print(f"Error loading from Drive: {e}")
        
        return super().load(default)
    
    def save(self, data):
        local_saved = super().save(data)
        
        if self.drive_service and self.drive_parent_id and local_saved:
            try:
                existing = self.drive_service.find_file(self.file_path.name, self.drive_parent_id)
                if existing:
                    self.drive_service.update_file(existing['id'], str(self.file_path))
                else:
                    self.drive_service.upload_file(str(self.file_path), parent_id=self.drive_parent_id)
            except Exception as e:
                print(f"Error saving to Drive: {e}")
        
        return local_saved


class ConfigManager:
    @staticmethod
    def load_config(file_path, default=None):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default or {}
    
    @staticmethod
    def save_config(file_path, config):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            return True
        except:
            return False
    
    @staticmethod
    def get_value(file_path, key, default=None):
        config = ConfigManager.load_config(file_path, {})
        return config.get(key, default)
    
    @staticmethod
    def set_value(file_path, key, value):
        config = ConfigManager.load_config(file_path, {})
        config[key] = value
        return ConfigManager.save_config(file_path, config)