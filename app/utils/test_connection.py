"""
Simple test of Supabase connection.
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for admin operations

print(f"URL: {supabase_url}")
print(f"Key (first 10 chars): {supabase_key[:10]}...")

try:
    # Create client
    supabase = create_client(supabase_url, supabase_key)
    
    # Try to get authenticated user
    auth_user = supabase.auth.get_user()
    print(f"\nConnection successful! Authenticated as: {auth_user}")
    
    # Try to check if we can access the SQL interface
    print("\nTrying to check Supabase health...")
    from supabase.lib.client_options import ClientOptions
    print(f"API URL: {supabase.rest_url}")
    
except Exception as e:
    print(f"\nError connecting to Supabase: {str(e)}")