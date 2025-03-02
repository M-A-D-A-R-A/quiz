from supabase import create_client, Client

class SupabaseApi:
    def __init__(self, url=None, key=None, **kwargs):
        self.url = url
        self.key = key
        self.client: Client = None
        
        if url and key:
            self.init_app(url, key, **kwargs)

    def init_app(self, url, key, **kwargs):
        """Initialize the Supabase client with the given URL and API key."""
        self.url = url
        self.key = key
        self.client = create_client(url, key)
        
        # Handle additional settings if needed
        if "headers" in kwargs:
            self.client.postgrest.headers.update(kwargs["headers"])
        
        if "auth" in kwargs and kwargs["auth"]:
            self.client.auth.sign_in_with_password(kwargs["auth"])  # Example for email-password auth
        
        return self 

    def get_client(self):
        """Returns the Supabase client instance."""
        if not self.client:
            raise ValueError("Supabase client is not initialized. Call init_app first.")
        return self.client
    
    def fetch_data(self, table, columns="*", filters=None, count_exact=False):
        """Fetches data from the specified table with optional column selection, filters, and supports counting."""
        if not self.client:
            raise ValueError("Supabase client is not initialized.")

        # If count_exact is True, override columns to fetch only the count
        query = self.client.table(table).select(columns if not count_exact else "count", count="exact")

        if filters:
            for col, value in filters.items():
                query = query.eq(col, value)

        response = query.execute()

        # If counting, return only the count
        if count_exact:
            return response.count

        return response
    
    def insert_data(self, table, data):
        """Inserts data into the specified table."""
        if not self.client:
            raise ValueError("Supabase client is not initialized.")
        
        return self.client.table(table).insert(data).execute()
    
    def update_data(self, table, filters, data):
        """Updates data in the specified table based on filters."""
        if not self.client:
            raise ValueError("Supabase client is not initialized.")
        
        query = self.client.table(table).update(data)
        
        for col, value in filters.items():
            query = query.eq(col, value)
        
        return query.execute()
    
    def delete_data(self, table, filters):
        """Deletes data from the specified table based on filters."""
        if not self.client:
            raise ValueError("Supabase client is not initialized.")
        
        query = self.client.table(table).delete()
        
        for col, value in filters.items():
            query = query.eq(col, value)
        
        return query.execute()
