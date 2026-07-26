"""
Seed script for LedgerDesk CA.
Run from the backend directory: python -m app.seed
"""
import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.auth.service import hash_password

async def seed():
    mongo_kwargs = {}
    if "mongodb+srv://" in settings.MONGODB_URL:
        mongo_kwargs["tlsAllowInvalidCertificates"] = True
    client = AsyncIOMotorClient(settings.MONGODB_URL, **mongo_kwargs)
    db = client[settings.DB_NAME]


    # --- Drop existing data for clean re-seed ---
    for col in ["users", "clients", "deadlines", "exceptions", "documents", "drafts", "reviews", "audit_logs", "demo_bookings"]:
        await db[col].drop()

    print("Seeding users...")
    users = [
        {"name": "N. Deshpande", "email": "partner@ledgerdesk.in", "password_hash": hash_password("partner123"), "firm_name": "Deshpande & Co CAs", "role": "partner", "created_at": datetime.utcnow()},
        {"name": "K. Shah", "email": "manager@ledgerdesk.in", "password_hash": hash_password("manager123"), "firm_name": "Deshpande & Co CAs", "role": "manager", "created_at": datetime.utcnow()},
        {"name": "Priya S", "email": "priya@ledgerdesk.in", "password_hash": hash_password("exec123"), "firm_name": "Deshpande & Co CAs", "role": "executive", "created_at": datetime.utcnow()},
        {"name": "Rohan V", "email": "rohan@ledgerdesk.in", "password_hash": hash_password("exec123"), "firm_name": "Deshpande & Co CAs", "role": "executive", "created_at": datetime.utcnow()},
    ]
    user_result = await db.users.insert_many(users)
    partner_id = str(user_result.inserted_ids[0])
    print(f"  Created {len(users)} users")

    print("Seeding clients...")
    today = datetime.utcnow()
    clients_data = [
        {"name": "Mangal Metals Pvt Ltd", "gstin": "27AAACM1234F1Z5", "pan": "AAACM1234F", "contact": "+91 98765 43210", "status": "active", "created_by": partner_id, "created_at": today},
        {"name": "Orbit Buildcon", "gstin": "27AABCO5678G1Z3", "pan": "AABCO5678G", "contact": "+91 98765 43211", "status": "active", "created_by": partner_id, "created_at": today},
        {"name": "Veda Plastics", "gstin": "27AACCV9012H1Z1", "pan": "AACCV9012H", "contact": "+91 98765 43212", "status": "active", "created_by": partner_id, "created_at": today},
        {"name": "Nova Realty LLP", "gstin": "27AADCN3456J1Z8", "pan": "AADCN3456J", "contact": "+91 98765 43213", "status": "active", "created_by": partner_id, "created_at": today},
        {"name": "Saffron Retail", "gstin": "27AAECS7890K1Z6", "pan": "AAECS7890K", "contact": "+91 98765 43214", "status": "active", "created_by": partner_id, "created_at": today},
        {"name": "Aster Healthcare", "gstin": "27AAFCA1234L1Z4", "pan": "AAFCA1234L", "contact": "+91 98765 43215", "status": "active", "created_by": partner_id, "created_at": today},
    ]
    client_result = await db.clients.insert_many(clients_data)
    cids = [str(cid) for cid in client_result.inserted_ids]
    print(f"  Created {len(clients_data)} clients")

    print("Seeding deadlines...")
    deadlines_data = [
        {"client_id": cids[0], "client_name": "Mangal Metals Pvt Ltd", "obligation": "GSTR-3B", "period": "Jun 2026", "due_date": today + timedelta(days=2), "owner": "Priya S", "status": "pending", "blocker": ""},
        {"client_id": cids[0], "client_name": "Mangal Metals Pvt Ltd", "obligation": "GSTR-1", "period": "Jun 2026", "due_date": today + timedelta(days=5), "owner": "Priya S", "status": "in_prep", "blocker": ""},
        {"client_id": cids[1], "client_name": "Orbit Buildcon", "obligation": "Notice reply", "period": "Q1 2026", "due_date": today - timedelta(days=1), "owner": "Rohan V", "status": "pending", "blocker": "Awaiting partner review"},
        {"client_id": cids[2], "client_name": "Veda Plastics", "obligation": "Tax audit", "period": "FY 2025-26", "due_date": today + timedelta(days=10), "owner": "K. Shah", "status": "in_review", "blocker": ""},
        {"client_id": cids[3], "client_name": "Nova Realty LLP", "obligation": "TDS return 24Q", "period": "Q1 2026", "due_date": today + timedelta(days=4), "owner": "Priya S", "status": "awaiting_docs", "blocker": "Salary register not received"},
        {"client_id": cids[4], "client_name": "Saffron Retail", "obligation": "GSTR-1", "period": "Jun 2026", "due_date": today + timedelta(days=1), "owner": "Rohan V", "status": "pending", "blocker": ""},
        {"client_id": cids[5], "client_name": "Aster Healthcare", "obligation": "Advance tax", "period": "Q1 2026", "due_date": today - timedelta(days=2), "owner": "K. Shah", "status": "overdue", "blocker": "Client not reachable"},
        {"client_id": cids[1], "client_name": "Orbit Buildcon", "obligation": "GSTR-3B", "period": "Jun 2026", "due_date": today + timedelta(days=3), "owner": "Rohan V", "status": "in_prep", "blocker": ""},
        {"client_id": cids[3], "client_name": "Nova Realty LLP", "obligation": "TDS return 26Q", "period": "Q1 2026", "due_date": today + timedelta(days=6), "owner": "Priya S", "status": "pending", "blocker": ""},
        {"client_id": cids[2], "client_name": "Veda Plastics", "obligation": "ROC annual return", "period": "FY 2025-26", "due_date": today + timedelta(days=30), "owner": "K. Shah", "status": "pending", "blocker": ""},
    ]
    await db.deadlines.insert_many(deadlines_data)
    print(f"  Created {len(deadlines_data)} deadlines")

    print("Seeding exceptions...")
    exceptions_data = [
        {"client_id": cids[0], "client_name": "Mangal Metals Pvt Ltd", "type": "GSTR-2A mismatch", "affected_entries": 14, "value_impact": "₹2.8L", "age": "3 days", "assigned_to": "Priya S", "next_action": "Ask client for purchase register", "state": "Open"},
        {"client_id": cids[4], "client_name": "Saffron Retail", "type": "Bank reconciliation break", "affected_entries": 7, "value_impact": "₹4.2L", "age": "5 days", "assigned_to": "Rohan V", "next_action": "Compare cash book with bank statement", "state": "In progress"},
        {"client_id": cids[3], "client_name": "Nova Realty LLP", "type": "TDS variance", "affected_entries": 3, "value_impact": "₹78K", "age": "2 days", "assigned_to": "Priya S", "next_action": "Verify 26AS vs TDS ledger", "state": "Open"},
        {"client_id": cids[1], "client_name": "Orbit Buildcon", "type": "Vendor mismatch", "affected_entries": 9, "value_impact": "₹1.5L", "age": "7 days", "assigned_to": "Rohan V", "next_action": "Supplier confirmation pending", "state": "Pending review"},
        {"client_id": cids[5], "client_name": "Aster Healthcare", "type": "GSTR-2A mismatch", "affected_entries": 22, "value_impact": "₹6.1L", "age": "1 day", "assigned_to": "Priya S", "next_action": "Match purchase invoices", "state": "Open"},
        {"client_id": cids[2], "client_name": "Veda Plastics", "type": "Ledger break", "affected_entries": 4, "value_impact": "₹92K", "age": "4 days", "assigned_to": "K. Shah", "next_action": "Check inter-branch transfers", "state": "In progress"},
    ]
    await db.exceptions.insert_many(exceptions_data)
    print(f"  Created {len(exceptions_data)} exceptions")

    print("Seeding documents...")
    documents_data = [
        {"client_id": cids[0], "client_name": "Mangal Metals Pvt Ltd", "requested_item": "Purchase register Jun-26", "related_task": "GSTR-3B prep", "requested_on": "11 Jul", "reminder_count": 2, "last_response": "Will send by EOD", "impact": "Filing at risk", "status": "Awaiting client", "file_path": ""},
        {"client_id": cids[3], "client_name": "Nova Realty LLP", "requested_item": "Salary register Q1", "related_task": "TDS 24Q filing", "requested_on": "08 Jul", "reminder_count": 3, "last_response": "No reply", "impact": "Filing blocked", "status": "Awaiting client", "file_path": ""},
        {"client_id": cids[1], "client_name": "Orbit Buildcon", "requested_item": "Supplier confirmations", "related_task": "Vendor recon", "requested_on": "10 Jul", "reminder_count": 1, "last_response": "Partial data shared", "impact": "Recon delayed", "status": "Partial received", "file_path": ""},
        {"client_id": cids[5], "client_name": "Aster Healthcare", "requested_item": "Bank statements Apr–Jun", "related_task": "Bank recon", "requested_on": "12 Jul", "reminder_count": 0, "last_response": "Just requested", "impact": "Recon pending", "status": "Awaiting client", "file_path": ""},
        {"client_id": cids[2], "client_name": "Veda Plastics", "requested_item": "Audit working papers FY26", "related_task": "Tax audit prep", "requested_on": "05 Jul", "reminder_count": 1, "last_response": "Shared Google Drive link", "impact": "Audit timeline", "status": "Received", "file_path": ""},
    ]
    await db.documents.insert_many(documents_data)
    print(f"  Created {len(documents_data)} document requests")

    print("Seeding drafts...")
    drafts_data = [
        {
            "client_id": cids[1], "client_name": "Orbit Buildcon",
            "matter": "GST SCN on ITC mismatch",
            "draft_type": "Notice reply",
            "content": "To,\nThe Assistant Commissioner (GST),\nWard 14, Mumbai\n\nSubject: Reply to Show Cause Notice — Ref 27A dated 02.07.2026\n\nSir/Madam,\n\nWith reference to the above-mentioned notice, we respectfully submit that the alleged ITC mismatch of ₹3.2L pertains to invoices that were reflected in GSTR-2A of the subsequent quarter (Jul–Sep 2025). The relevant supplier confirmations, purchase invoices, and GSTR-2A extracts are annexed herewith as supporting evidence.\n\nWe request your kind consideration of the enclosed documentation.\n\nYours faithfully,\nFor Orbit Buildcon",
            "prepared_by": "Rohan V", "reviewer": "N. Deshpande",
            "state": "Draft ready", "due_by": "18 Jul",
            "comments": [
                {"author": "N. Deshpande", "text": "Add reconciliation summary as Annexure A and CESTAT citation.", "timestamp": today - timedelta(hours=5)}
            ],
            "version": 0.9, "created_at": today - timedelta(days=2)
        },
        {
            "client_id": cids[0], "client_name": "Mangal Metals Pvt Ltd",
            "matter": "GSTR-1 reconciliation summary",
            "draft_type": "Reconciliation note",
            "content": "Reconciliation summary for Mangal Metals GSTR-1 vs books for June 2026.\n\nTotal invoices in books: 142\nTotal invoices in GSTR-1: 139\nVariance: 3 invoices (₹42,800)\n\nMissing invoices identified:\n1. Invoice #MM-2026-0891 — ₹18,200 (dated 28 Jun)\n2. Invoice #MM-2026-0903 — ₹14,600 (dated 29 Jun)\n3. Invoice #MM-2026-0910 — ₹10,000 (dated 30 Jun)\n\nAll three are late-dated invoices that need to be included in the July GSTR-1 filing.",
            "prepared_by": "Priya S", "reviewer": "K. Shah",
            "state": "In progress", "due_by": "20 Jul",
            "comments": [],
            "version": 1.0, "created_at": today - timedelta(days=1)
        }
    ]
    await db.drafts.insert_many(drafts_data)
    print(f"  Created {len(drafts_data)} drafts")

    print("Seeding reviews...")
    reviews_data = [
        {
            "work_item_id": "seed-review-1", "work_item_type": "Notice reply draft",
            "client_id": cids[1], "client_name": "Orbit Buildcon",
            "item_name": "GST SCN reply v0.9", "submitted_by": "Rohan V",
            "reviewer": "N. Deshpande", "status": "Awaiting partner",
            "comments": [
                {"author": "K. Shah", "text": "Checked factual accuracy. Recommend partner review.", "timestamp": today - timedelta(hours=8)}
            ],
            "risk_flag": "High", "timestamp": today - timedelta(hours=6),
            "export_state": "Not exported", "version": "v0.9"
        },
        {
            "work_item_id": "seed-review-2", "work_item_type": "GST reconciliation summary",
            "client_id": cids[0], "client_name": "Mangal Metals Pvt Ltd",
            "item_name": "GSTR-3B review pack v1.3", "submitted_by": "Priya S",
            "reviewer": "N. Deshpande", "status": "Approved",
            "comments": [
                {"author": "N. Deshpande", "text": "Looks good. Approved for filing.", "timestamp": today - timedelta(hours=3)}
            ],
            "risk_flag": "Medium", "timestamp": today - timedelta(hours=2),
            "export_state": "Exported", "version": "v1.3"
        },
        {
            "work_item_id": "seed-review-3", "work_item_type": "Audit workpaper pack",
            "client_id": cids[2], "client_name": "Veda Plastics",
            "item_name": "Tax audit workpapers v2.1", "submitted_by": "K. Shah",
            "reviewer": "N. Deshpande", "status": "Approved",
            "comments": [],
            "risk_flag": "Low", "timestamp": today - timedelta(hours=12),
            "export_state": "Exported", "version": "v2.1"
        },
        {
            "work_item_id": "seed-review-4", "work_item_type": "TDS reconciliation summary",
            "client_id": cids[3], "client_name": "Nova Realty LLP",
            "item_name": "TDS recon note v1.1", "submitted_by": "Priya S",
            "reviewer": "N. Deshpande", "status": "Approved",
            "comments": [],
            "risk_flag": "Medium", "timestamp": today - timedelta(hours=18),
            "export_state": "Exported", "version": "v1.1"
        },
        {
            "work_item_id": "seed-review-5", "work_item_type": "GST reconciliation summary",
            "client_id": cids[4], "client_name": "Saffron Retail",
            "item_name": "GSTR-1 recon summary v1.0", "submitted_by": "Priya S",
            "reviewer": "K. Shah", "status": "Awaiting manager",
            "comments": [],
            "risk_flag": "Medium", "timestamp": today - timedelta(hours=1),
            "export_state": "Not exported", "version": "v1.0"
        },
    ]
    await db.reviews.insert_many(reviews_data)
    print(f"  Created {len(reviews_data)} review items")

    print("\n✅ Seed complete!")
    print("──────────────────────────────────────────")
    print("Login credentials:")
    print("  Partner:   partner@ledgerdesk.in / partner123")
    print("  Manager:   manager@ledgerdesk.in / manager123")
    print("  Executive: priya@ledgerdesk.in   / exec123")
    print("  Executive: rohan@ledgerdesk.in   / exec123")
    print("──────────────────────────────────────────")

    client.close()

if __name__ == "__main__":
    asyncio.run(seed())
