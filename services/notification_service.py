import json
import datetime
from pathlib import Path


try:
    from plyer import notification as os_notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    print("plyer not installed - using in-app notifications only")


class NotificationService:
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("lms_data")
        self.data_dir.mkdir(exist_ok=True)
        self.notifications_file = self.data_dir / "notifications.json"
        self.notifications = self.load_notifications()
    
    def load_notifications(self):
        if self.notifications_file.exists():
            try:
                with open(self.notifications_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("notifications", [])
            except:
                pass
        return []
    
    def save_notifications(self):
        with open(self.notifications_file, 'w', encoding='utf-8') as f:
            json.dump({"notifications": self.notifications}, f, indent=2, ensure_ascii=False)
    
    def send_notification(self, title: str, message: str, student_email: str = None, assignment_id: str = None, notification_type: str = "info"):
        
        notification_record = {
            "id": str(datetime.datetime.now().timestamp()),
            "type": notification_type,
            "title": title,
            "message": message,
            "student_email": student_email,
            "assignment_id": assignment_id,
            "created_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            "read": False
        }
        self.notifications.append(notification_record)
        self.save_notifications()
        
        if PLYER_AVAILABLE:
            try:
                os_notification.notify(
                    title=title,
                    message=message,
                    app_name="LMS Assignment Manager",
                    timeout=10
                )
                return True
            except Exception as e:
                print(f"OS notification failed: {e}")
        
        return False
    
    def notify_new_assignment(self, assignment: dict, students: list):
        
        title = f"New Assignment: {assignment.get('title', 'Untitled')}"
        message = f"Subject: {assignment.get('subject', 'N/A')}\nDeadline: {assignment.get('deadline', 'No deadline')}"
        
        os_notified = False
        
        for student in students:
            student_email = student.get('email')
            self.send_notification(
                title=title,
                message=message,
                student_email=student_email,
                assignment_id=assignment.get('id'),
                notification_type="new_assignment"
            )
            
            if not os_notified and PLYER_AVAILABLE:
                try:
                    os_notification.notify(
                        title=title,
                        message=f"{message}\nAssigned to {len(students)} students",
                        app_name="LMS Assignment Manager",
                        timeout=10
                    )
                    os_notified = True
                except:
                    pass
    
    def notify_deadline_reminder(self, assignment: dict, student_email: str, hours_remaining: int):
        
        title = f"⏰ Deadline Reminder: {assignment.get('title', 'Assignment')}"
        message = f"Only {hours_remaining} hours remaining to submit!"
        
        self.send_notification(
            title=title,
            message=message,
            student_email=student_email,
            assignment_id=assignment.get('id'),
            notification_type="deadline_reminder"
        )
    
    def notify_submission_received(self, assignment: dict, student_name: str):
        
        title = f"Submission Received"
        message = f"{student_name} submitted: {assignment.get('title', 'Assignment')}"
        
        self.send_notification(
            title=title,
            message=message,
            assignment_id=assignment.get('id'),
            notification_type="submission_received"
        )
    
    def notify_grade_posted(self, assignment: dict, student_email: str, grade: str):
        
        title = f"Grade Posted: {assignment.get('title', 'Assignment')}"
        message = f"Your grade: {grade}"
        
        self.send_notification(
            title=title,
            message=message,
            student_email=student_email,
            assignment_id=assignment.get('id'),
            notification_type="grade_posted"
        )
    
    def get_notifications_for_student(self, student_email: str):
        
        return [n for n in self.notifications 
                if n.get('student_email') == student_email or n.get('student_email') is None]
    
    def get_unread_count(self, student_email: str = None):
        
        if student_email:
            relevant = self.get_notifications_for_student(student_email)
        else:
            relevant = self.notifications
        return sum(1 for n in relevant if not n.get('read', False))
    
    def mark_as_read(self, notification_id: str):
        
        for n in self.notifications:
            if n.get('id') == notification_id:
                n['read'] = True
                self.save_notifications()
                return True
        return False
    
    def mark_all_as_read(self, student_email: str = None):
        
        for n in self.notifications:
            if student_email is None or n.get('student_email') == student_email:
                n['read'] = True
        self.save_notifications()
    
    def clear_old_notifications(self, days: int = 30):
        
        cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
        self.notifications = [
            n for n in self.notifications
            if datetime.datetime.strptime(n['created_at'], '%Y-%m-%d %H:%M') > cutoff
        ]
        self.save_notifications()
