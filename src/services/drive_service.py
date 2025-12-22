from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
from utils.base_service import BaseService
from utils.drive_helpers import DriveQueryBuilder, DriveOperations, DriveRequestBuilder, DriveFileFields
from utils.file_operations import FileOperations


class DriveService(BaseService):
    
    def __init__(self, service, cache_ttl=300, max_retries=3):
        super().__init__(cache_ttl, max_retries, retry_delay=1)
        self.service = service
    
    def _execute_file_list_query(self, query, page_size=100, page_token=None, fields="nextPageToken, files(id, name, mimeType, modifiedTime, size, owners)", order_by="folder,name"):
        def make_request():
            return DriveRequestBuilder.list_request(
                self.service, query, page_size, page_token, fields, order_by
            ).execute()
        
        return self._retry_request(make_request, f"list_query({query[:50]})")
    
    def list_files(self, folder_id='root', page_size=100, page_token=None, use_cache=True):
        cache_key = f"files_{folder_id}_{page_size}_{page_token}"
        
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                print(f"Cache hit for {cache_key}")
                return cached
        
        query = DriveQueryBuilder().in_parents(folder_id).not_trashed().build()
        result = self._execute_file_list_query(query, page_size, page_token)
        
        if result is not None:
            formatted_result = {
                'files': result.get('files', []),
                'nextPageToken': result.get('nextPageToken', None)
            }
            self._set_cache(cache_key, formatted_result)
            return formatted_result
        
        return None
    
    def search_files(self, query_text, folder_id=None, use_cache=False):
        cache_key = f"search_{query_text}_{folder_id}"
        
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached
        
        query_builder = DriveQueryBuilder().name_contains(query_text).not_trashed()
        if folder_id:
            query_builder.in_parents(folder_id)
        
        result = self._execute_file_list_query(
            query_builder.build(), 
            page_size=50, 
            fields="files(id, name, mimeType, modifiedTime, parents)"
        )
        files = result.get('files', []) if result else []
        
        if use_cache and files:
            self._set_cache(cache_key, files)
        
        return files
    
    def get_file_info(self, file_id, use_cache=True):
        cache_key = f"fileinfo_{file_id}"
        
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached
        
        def make_request():
            return DriveRequestBuilder.get_request(self.service, file_id).execute()
        
        file = self._retry_request(make_request, f"get_file_info({file_id})")
        
        if file is not None:
            self._set_cache(cache_key, file)
        
        return file

    def resolve_drive_link(self, link):
        from utils.validators import StringUtils
        file_id = StringUtils.extract_id_from_url(link)
        
        if not file_id:
            print(f"Could not extract file ID from link: {link}")
            return None, None
        
        info = self.get_file_info(file_id)
        
        if not info:
            print(f"Could not retrieve file info for ID: {file_id}")
            return None, None
        
        return file_id, info
    
    def _execute_file_mutation(self, operation_name, request_func, parent_id=None):
        result = self._retry_request(request_func, operation_name)
        
        if result and parent_id:
            self._invalidate_cache(parent_id)
        
        return result
    
    def create_folder(self, folder_name, parent_id='root'):
        def make_request():
            return DriveRequestBuilder.create_folder_request(
                self.service, folder_name, parent_id
            ).execute()
        
        return self._execute_file_mutation(f"create_folder({folder_name})", make_request, parent_id)
    
    def upload_file(self, file_path, parent_id='root', file_name=None, progress_callback=None):
        try:
            if not file_name:
                import os
                file_name = os.path.basename(file_path)
                
            file_metadata = {
                'name': file_name,
                'parents': [parent_id]
            }
            
            media = MediaFileUpload(file_path, resumable=True)
            
            request = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, mimeType, size, webViewLink, parents'
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status and progress_callback:
                    progress_callback(status.resumable_progress, status.total_size)
            
            self._invalidate_cache(parent_id)
            
            return response
            
        except Exception as error:
            print(f"Error uploading file: {error}")
            return None
    
    def update_file(self, file_id, file_path, new_name=None):
        try:
            file_metadata = {}
            if new_name:
                file_metadata['name'] = new_name
            
            media = MediaFileUpload(file_path, resumable=True)
            
            updated_file = self.service.files().update(
                fileId=file_id,
                body=file_metadata,
                media_body=media,
                fields='id, name, mimeType, modifiedTime'
            ).execute()
            
            self._invalidate_cache(file_id)
            return updated_file
        except Exception as error:
            print(f"Error updating file: {error}")
            return None

    def read_file_content(self, file_id):
        try:
            request = self.service.files().get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            return file.getvalue().decode('utf-8')
        except Exception as error:
            print(f"Error reading file content: {error}")
            return None

    def find_file(self, name, parent_id):
        return DriveOperations.find_by_name(self.service, name, parent_id)

    def move_file(self, file_id, new_parent_id):
        def make_request():
            file = self.service.files().get(fileId=file_id, fields='parents').execute()
            previous_parents = ",".join(file.get('parents', []))
            
            return self.service.files().update(
                fileId=file_id,
                addParents=new_parent_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()
        
        updated_file = self._retry_request(make_request, f"move_file({file_id})")
        
        if updated_file:
            file = self.service.files().get(fileId=file_id, fields='parents').execute()
            for parent in file.get('parents', []):
                self._invalidate_cache(parent)
            self._invalidate_cache(new_parent_id)
        
        return updated_file
    
    def rename_file(self, file_id, new_name):
        def make_request():
            file_metadata = {'name': new_name}
            return self.service.files().update(
                fileId=file_id,
                body=file_metadata,
                fields='id, name, parents'
            ).execute()
        
        updated_file = self._retry_request(make_request, f"rename_file({file_id})")
        
        if updated_file:
            for parent in updated_file.get('parents', []):
                self._invalidate_cache(parent)
            self._invalidate_cache(file_id)
        
        return updated_file
    
    def delete_file(self, file_id):
        file_info = self.get_file_info(file_id, use_cache=False)
        
        def make_request():
            self.service.files().delete(fileId=file_id).execute()
            return True
        
        success = self._retry_request(make_request, f"delete_file({file_id})")
        
        if success:
            if file_info and 'parents' in file_info:
                for parent in file_info['parents']:
                    self._invalidate_cache(parent)
            self._invalidate_cache(file_id)
            return True
        
        return False
    
    def get_folder_tree(self, folder_id='root', max_depth=2, current_depth=0):
        if current_depth >= max_depth:
            return None
        
        folders = DriveOperations.list_folders_only(self.service, folder_id)
        
        for folder in folders:
            folder['children'] = self.get_folder_tree(
                folder['id'], 
                max_depth, 
                current_depth + 1
            )
        
        return folders