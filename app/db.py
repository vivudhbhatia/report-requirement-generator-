from supabase import create_client
import os
from datetime import datetime

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

retry_queue = []

def save_to_supabase(row, prompt=None, response=None):
    data = {
        "report_id": row["report_id"],
        "schedule": row["schedule"],
        "line_number": row["line_number"],
        "item_name": row["item_name"],
        "report_instructions": row["report_instructions"],
        "product": row["product"],
        "logical_data_elements": row["logical_data_elements"],
        "regulatory_logic": row["regulatory_logic"],
        "processed_at": datetime.utcnow().isoformat(),
        "llm_prompt": prompt,
        "llm_response": response
    }
    try:
        response = supabase.table("report_brd").insert(data).execute()
        print(f"[✅ INSERTED] {row['line_number']}: {row['item_name']}")
    except Exception as e:
        print(f"[❌ FAILED] {row['line_number']}: {e}")
        retry_queue.append(row)

def query_supabase(term):
    query = supabase.table("report_brd").select("*").ilike("item_name", f"%{term}%").execute()
    return query.data if query.data else []

def get_all_line_items(report_id=None):
    query = supabase.table("report_brd").select("*")
    if report_id:
        query = query.eq("report_id", report_id)
    result = query.execute()
    return result.data if result.data else []

def get_failed_queue():
    return retry_queue
