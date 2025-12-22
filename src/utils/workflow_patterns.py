import datetime
from typing import Callable, Any, Dict, List


class WorkflowStep:
    def __init__(self, name, action, on_success=None, on_error=None, rollback=None):
        self.name = name
        self.action = action
        self.on_success = on_success
        self.on_error = on_error
        self.rollback = rollback
        self.result = None
    
    def execute(self):
        try:
            self.result = self.action()
            if self.on_success:
                self.on_success(self.result)
            return True, self.result
        except Exception as e:
            if self.on_error:
                self.on_error(e)
            return False, e
    
    def undo(self):
        if self.rollback:
            try:
                self.rollback(self.result)
                return True
            except:
                return False
        return False


class Workflow:
    def __init__(self, name):
        self.name = name
        self.steps = []
        self.completed_steps = []
        self.failed = False
    
    def add_step(self, step):
        self.steps.append(step)
        return self
    
    def execute(self):
        for step in self.steps:
            success, result = step.execute()
            
            if success:
                self.completed_steps.append(step)
            else:
                self.failed = True
                self.rollback()
                return False, result
        
        return True, None
    
    def rollback(self):
        for step in reversed(self.completed_steps):
            step.undo()


class EventBus:
    def __init__(self):
        self._subscribers = {}
    
    def subscribe(self, event_type, callback):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type, callback):
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)
    
    def emit(self, event_type, data=None):
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                callback(data)


class TaskQueue:
    def __init__(self):
        self._queue = []
        self._results = {}
    
    def add_task(self, task_id, task_func, priority=0):
        self._queue.append({
            'id': task_id,
            'func': task_func,
            'priority': priority,
            'status': 'pending'
        })
        self._queue.sort(key=lambda x: x['priority'], reverse=True)
    
    def execute_all(self):
        results = []
        
        for task in self._queue:
            if task['status'] == 'pending':
                try:
                    result = task['func']()
                    task['status'] = 'completed'
                    self._results[task['id']] = result
                    results.append({'id': task['id'], 'success': True, 'result': result})
                except Exception as e:
                    task['status'] = 'failed'
                    self._results[task['id']] = e
                    results.append({'id': task['id'], 'success': False, 'error': e})
        
        return results
    
    def get_result(self, task_id):
        return self._results.get(task_id)
    
    def clear(self):
        self._queue = []
        self._results = {}


class DataTransformer:
    @staticmethod
    def transform_list(items, mapping):
        return [{mapping.get(k, k): v for k, v in item.items()} for item in items]
    
    @staticmethod
    def filter_list(items, predicate):
        return [item for item in items if predicate(item)]
    
    @staticmethod
    def group_by(items, key):
        groups = {}
        for item in items:
            group_key = item.get(key)
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(item)
        return groups
    
    @staticmethod
    def aggregate(items, key, aggregator='sum'):
        values = [item.get(key) for item in items if item.get(key) is not None]
        
        if aggregator == 'sum':
            return sum(values)
        elif aggregator == 'avg':
            return sum(values) / len(values) if values else 0
        elif aggregator == 'max':
            return max(values) if values else None
        elif aggregator == 'min':
            return min(values) if values else None
        elif aggregator == 'count':
            return len(values)
        
        return None


class BatchProcessor:
    def __init__(self, batch_size=10):
        self.batch_size = batch_size
    
    def process(self, items, processor_func, on_batch_complete=None):
        results = []
        
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            
            batch_results = []
            for item in batch:
                try:
                    result = processor_func(item)
                    batch_results.append({'success': True, 'result': result, 'item': item})
                except Exception as e:
                    batch_results.append({'success': False, 'error': e, 'item': item})
            
            results.extend(batch_results)
            
            if on_batch_complete:
                on_batch_complete(batch_results, i // self.batch_size + 1)
        
        return results


class ConditionalExecutor:
    def __init__(self):
        self.conditions = []
    
    def when(self, condition, action):
        self.conditions.append((condition, action))
        return self
    
    def otherwise(self, action):
        self.default_action = action
        return self
    
    def execute(self, context=None):
        for condition, action in self.conditions:
            if condition(context):
                return action(context)
        
        if hasattr(self, 'default_action'):
            return self.default_action(context)
        
        return None


class RetryStrategy:
    @staticmethod
    def exponential_backoff(func, max_retries=3, base_delay=1, max_delay=60):
        import time
        
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                delay = min(base_delay * (2 ** attempt), max_delay)
                time.sleep(delay)
    
    @staticmethod
    def linear_backoff(func, max_retries=3, delay=1):
        import time
        
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(delay)
    
    @staticmethod
    def immediate_retry(func, max_retries=3):
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e


class RateLimiter:
    def __init__(self, max_calls, time_window):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def can_execute(self):
        now = datetime.datetime.now()
        cutoff = now - datetime.timedelta(seconds=self.time_window)
        
        self.calls = [call_time for call_time in self.calls if call_time > cutoff]
        
        return len(self.calls) < self.max_calls
    
    def execute(self, func):
        if self.can_execute():
            self.calls.append(datetime.datetime.now())
            return func()
        else:
            raise Exception("Rate limit exceeded")
    
    def wait_and_execute(self, func):
        import time
        
        while not self.can_execute():
            time.sleep(0.1)
        
        return self.execute(func)


class Pipeline:
    def __init__(self, initial_data=None):
        self.data = initial_data
        self.steps = []
    
    def pipe(self, transform_func):
        self.steps.append(transform_func)
        return self
    
    def execute(self):
        result = self.data
        
        for step in self.steps:
            result = step(result)
        
        return result
    
    def add_logger(self, step_name):
        def log_step(data):
            print(f"[Pipeline] {step_name}: {type(data)}")
            return data
        
        self.steps.append(log_step)
        return self


class CommandPattern:
    class Command:
        def execute(self):
            raise NotImplementedError
        
        def undo(self):
            raise NotImplementedError
    
    class CommandHistory:
        def __init__(self):
            self.history = []
            self.current_index = -1
        
        def execute(self, command):
            command.execute()
            
            self.history = self.history[:self.current_index + 1]
            self.history.append(command)
            self.current_index += 1
        
        def undo(self):
            if self.current_index >= 0:
                command = self.history[self.current_index]
                command.undo()
                self.current_index -= 1
        
        def redo(self):
            if self.current_index < len(self.history) - 1:
                self.current_index += 1
                command = self.history[self.current_index]
                command.execute()
        
        def can_undo(self):
            return self.current_index >= 0
        
        def can_redo(self):
            return self.current_index < len(self.history) - 1