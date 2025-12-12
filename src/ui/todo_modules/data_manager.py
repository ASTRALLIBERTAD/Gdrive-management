import json
from pathlib import Path


class DataManager:
    
    def __init__(self, data_dir: Path, drive_service=None):
        self.data_dir = data_dir
        self.drive_service = drive_service
        self.lms_root_id = self._load_lms_root_id()
        
        self.assignments_file = data_dir / "assignments.json"
        self.students_file = data_dir / "students.json"
        self.submissions_file = data_dir / "submissions.json"
    
    def _load_lms_root_id(self):
        
        import os
        config_file = "lms_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    return config.get("lms_root_id")
            except:
                pass
        return None
    
    def load_json(self, filepath, default=None):
        
        if self.drive_service and self.lms_root_id:
            filename = filepath.name
            try:
                file = self.drive_service.find_file(filename, self.lms_root_id)
                if file:
                    content = self.drive_service.read_file_content(file['id'])
                    if content:
                        return json.loads(content)
            except Exception as e:
                print(f"Error loading from Drive: {e}")
        
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return default if default is not None else []
    
    def save_json(self, filepath, data):
    
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving local: {e}")
        
        
        if self.drive_service and self.lms_root_id:
            filename = filepath.name
            try:
                existing = self.drive_service.find_file(filename, self.lms_root_id)
                if existing:
                    self.drive_service.update_file(existing['id'], str(filepath))
                else:
                    self.drive_service.upload_file(str(filepath), parent_id=self.lms_root_id)
            except Exception as e:
                print(f"Error saving to Drive: {e}")
    
    def load_assignments(self):
        import datetime
        assignments = self.load_json(self.assignments_file, [])
        
        modified = False
        for i, assignment in enumerate(assignments):
            if 'id' not in assignment:
                assignment['id'] = str(datetime.datetime.now().timestamp()) + str(i)
                modified = True
        
        if modified:
            self.save_json(self.assignments_file, assignments)
        
        return assignments
    
    def load_students(self):
        return self.load_json(self.students_file, [])
    
    def load_submissions(self):
        return self.load_json(self.submissions_file, [])
    
    def save_assignments(self, assignments):
        self.save_json(self.assignments_file, assignments)
    
    def save_students(self, students):
        self.save_json(self.students_file, students)
    
    def save_submissions(self, submissions):
        self.save_json(self.submissions_file, submissions)