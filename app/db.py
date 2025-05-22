from supabase import create_client
import os
from datetime import datetime

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_brd_row(row, prompt, response):
    data = {
        "report_id": row["report_id"],
        "schedule": row["schedule"],
        "line_item": row["line_item"],
        "line_title": row["line_title"],
        "instructions": row["instructions"],
        "general_instructions": row.get("general_instructions", "N/A"),
        "glossary": row.get("glossary", []),
        "asc_references": row.get("asc_references", []),
        "prompt_used": prompt,
        "openai_response": response,
        "processed_at": datetime.utcnow().isoformat(),
        "status": "processed"
    }
    try:
        supabase.table("report_brd").insert(data).execute()
    except Exception as e:
        print("❌ Supabase insert failed:", e)
