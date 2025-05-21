from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_to_supabase(row):
    data = {
        "report_id": row["report_id"],
        "schedule": row["schedule"],
        "line_number": row["line_number"],
        "item_name": row["item_name"],
        "report_instructions": row["report_instructions"],
        "product": row["product"],
        "logical_data_elements": row["logical_data_elements"],
        "regulatory_logic": row["regulatory_logic"]
    }
    supabase.table("report_brd").insert(data).execute()

def query_supabase(term):
    query = supabase.table("report_brd").select("*").ilike("item_name", f"%{term}%").execute()
    return query.data if query.data else []
