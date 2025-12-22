class DriveQueryBuilder:
    def __init__(self):
        self.conditions = []
    
    def in_parents(self, parent_id):
        self.conditions.append(f"'{parent_id}' in parents")
        return self
    
    def not_trashed(self):
        self.conditions.append("trashed=false")
        return self
    
    def name_equals(self, name):
        escaped_name = name.replace("'", "\\'")
        self.conditions.append(f"name = '{escaped_name}'")
        return self
    
    def name_contains(self, query):
        escaped_query = query.replace("'", "\\'")
        self.conditions.append(f"name contains '{escaped_query}'")
        return self
    
    def mime_type(self, mime_type):
        self.conditions.append(f"mimeType='{mime_type}'")
        return self
    
    def is_folder(self):
        self.mime_type('application/vnd.google-apps.folder')
        return self
    
    def modified_after(self, date):
        self.conditions.append(f"modifiedTime > '{date}'")
        return self
    
    def build(self):
        return " and ".join(self.conditions) if self.conditions else None
    
    def reset(self):
        self.conditions = []
        return self


class DriveFileFields:
    BASIC = "id, name, mimeType"
    STANDARD = "id, name, mimeType, modifiedTime, size"
    DETAILED = "id, name, mimeType, modifiedTime, size, owners, parents, webViewLink"
    ALL = "id, name, mimeType, size, createdTime, modifiedTime, owners, parents, webViewLink"
    
    @staticmethod
    def with_page_token(fields):
        return f"nextPageToken, files({fields})"


class DriveRequestBuilder:
    @staticmethod
    def list_request(service, query=None, page_size=100, page_token=None, fields=None, order_by="folder,name"):
        params = {
            'pageSize': page_size,
            'fields': fields or DriveFileFields.with_page_token(DriveFileFields.STANDARD),
            'orderBy': order_by
        }
        
        if query:
            params['q'] = query
        if page_token:
            params['pageToken'] = page_token
        
        return service.files().list(**params)
    
    @staticmethod
    def get_request(service, file_id, fields=None):
        return service.files().get(
            fileId=file_id,
            fields=fields or DriveFileFields.DETAILED
        )
    
    @staticmethod
    def create_folder_request(service, folder_name, parent_id):
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        return service.files().create(
            body=file_metadata,
            fields='id, name'
        )


class DriveOperations:
    @staticmethod
    def execute_with_pagination(service, query, max_results=None, **kwargs):
        results = []
        page_token = None
        
        while True:
            request = DriveRequestBuilder.list_request(
                service, 
                query=query, 
                page_token=page_token,
                **kwargs
            )
            response = request.execute()
            
            files = response.get('files', [])
            results.extend(files)
            
            if max_results and len(results) >= max_results:
                return results[:max_results]
            
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        
        return results
    
    @staticmethod
    def find_by_name(service, name, parent_id, mime_type=None):
        query_builder = DriveQueryBuilder()
        query_builder.name_equals(name).in_parents(parent_id).not_trashed()
        
        if mime_type:
            query_builder.mime_type(mime_type)
        
        request = DriveRequestBuilder.list_request(
            service,
            query=query_builder.build(),
            page_size=1
        )
        
        result = request.execute()
        files = result.get('files', [])
        return files[0] if files else None
    
    @staticmethod
    def list_folders_only(service, parent_id):
        query = DriveQueryBuilder().in_parents(parent_id).is_folder().not_trashed().build()
        return DriveOperations.execute_with_pagination(service, query)