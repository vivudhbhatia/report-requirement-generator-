from supabase import create_client
import os

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def save_to_supabase(record):
    data, count = supabase.table("report_brd").insert(record).execute()
    return data
