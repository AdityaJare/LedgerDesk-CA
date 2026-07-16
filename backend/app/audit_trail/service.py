from datetime import datetime
from typing import Optional

async def log_audit_event(
    db,
    user_id: Optional[str],
    action: str,
    resource_type: str,
    resource_id: Optional[str],
    details: str,
    ip_address: Optional[str] = None
):
    log_entry = {
        "user_id": user_id,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "details": details,
        "timestamp": datetime.utcnow(),
        "ip_address": ip_address
    }
    await db.audit_logs.insert_one(log_entry)
