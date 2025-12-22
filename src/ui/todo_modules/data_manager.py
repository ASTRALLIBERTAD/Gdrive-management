from pathlib import Path
from utils.data_managers import SyncedDataManager, ConfigManager
import datetime


class DataManager:
    
    def __init__(self, data_dir, drive_service=None):
        self.data_dir = Path(data_dir) if isinstance(data_dir, str) else data_dir
        self.drive_service = drive_service
        self.lms_root_id = self._load_lms_root_id()
        
        self.assignments_mgr = SyncedDataManager(
            self.data_dir, 
            "assignments.json", 
            drive_service, 
            self.lms_root_id
        )
        self.students_mgr = SyncedDataManager(
            self.data_dir, 
            "students.json", 
            drive_service, 
            self.lms_root_id
        )
        self.submissions_mgr = SyncedDataManager(
            self.data_dir, 
            "submissions.json", 
            drive_service, 
            self.lms_root_id
        )
    
    def _load_lms_root_id(self):
        return ConfigManager.get_value("lms_config.json", "lms_root_id")
    
    def load_assignments(self):
        assignments = self.assignments_mgr.load([])
        
        modified = False
        for i, assignment in enumerate(assignments):
            if 'id' not in assignment:
                assignment['id'] = str(datetime.datetime.now().timestamp()) + str(i)
                modified = True
        
        if modified:
            self.save_assignments(assignments)
        
        return assignments
    
    def load_students(self):
        return self.students_mgr.load([])
    
    def load_submissions(self):
        return self.submissions_mgr.load([])
    
    def save_assignments(self, assignments):
        self.assignments_mgr.save(assignments)
    
    def save_students(self, students):
        self.students_mgr.save(students)
    
    def save_submissions(self, submissions):
        self.submissions_mgr.save(submissions)