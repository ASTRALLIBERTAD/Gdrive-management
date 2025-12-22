import re
from datetime import datetime


class Validator:
    @staticmethod
    def is_empty(value):
        return not value or not str(value).strip()
    
    @staticmethod
    def validate_email(email):
        if not email:
            return False, "Email is required"
        
        if "@" not in email or "." not in email:
            return False, "Invalid email format"
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Invalid email format"
        
        return True, ""
    
    @staticmethod
    def validate_required_fields(fields_dict):
        errors = []
        for field_name, value in fields_dict.items():
            if Validator.is_empty(value):
                errors.append(f"{field_name} is required")
        return errors
    
    @staticmethod
    def is_past_datetime(dt):
        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt)
            except:
                return False
        return dt <= datetime.now()
    
    @staticmethod
    def validate_date_range(start_date, end_date):
        if start_date >= end_date:
            return False, "End date must be after start date"
        return True, ""


class StringUtils:
    @staticmethod
    def truncate(text, max_length, suffix="..."):
        if not text:
            return ""
        text = str(text)
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def extract_id_from_url(url, patterns=None):
        if not patterns:
            patterns = [
                r"/folders/([a-zA-Z0-9_-]+)",
                r"/file/d/([a-zA-Z0-9_-]+)",
                r"[?&]id=([a-zA-Z0-9_-]+)"
            ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        if len(url) > 20 and "/" not in url:
            return url
        
        return None
    
    @staticmethod
    def sanitize_filename(filename):
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename


class DateTimeUtils:
    @staticmethod
    def format_datetime(dt, format_str='%Y-%m-%d %H:%M'):
        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt)
            except:
                return dt
        return dt.strftime(format_str)
    
    @staticmethod
    def parse_datetime(dt_string, format_str='%Y-%m-%d %H:%M'):
        try:
            return datetime.strptime(dt_string, format_str)
        except:
            try:
                return datetime.fromisoformat(dt_string)
            except:
                return None
    
    @staticmethod
    def time_until(target_dt):
        if isinstance(target_dt, str):
            target_dt = DateTimeUtils.parse_datetime(target_dt)
        
        if not target_dt:
            return "Invalid date"
        
        now = datetime.now()
        remaining = target_dt - now
        
        if remaining.total_seconds() <= 0:
            return "Overdue"
        
        days = remaining.days
        hours = remaining.seconds // 3600
        minutes = (remaining.seconds % 3600) // 60
        
        if days > 0:
            return f"⏱️ {days}d {hours}h remaining"
        elif hours > 0:
            return f"⏱️ {hours}h {minutes}m remaining"
        else:
            return f"⏱️ {minutes}m remaining"
    
    @staticmethod
    def time_since(past_dt):
        if isinstance(past_dt, str):
            past_dt = DateTimeUtils.parse_datetime(past_dt)
        
        if not past_dt:
            return "Invalid date"
        
        now = datetime.now()
        diff = now - past_dt
        
        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        
        if days > 0:
            return f"{days}d {hours}h ago"
        elif hours > 0:
            return f"{hours}h {minutes}m ago"
        else:
            return f"{minutes}m ago"