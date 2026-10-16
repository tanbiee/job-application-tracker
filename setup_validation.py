from datetime import date

from database import db, applications
from pymongo.errors import PyMongoError

ALLOWED_STATUSES = [
    "Applied",
    "Online Assesment",
    "Interview",
    "Offer",
    "Rejected"
]

# prepare older doc that may be mising optional fields or dates
# preserve existing values whenever they are present.

for document in applications.find():
    updates = {}

    if not document.get("applied_date"):
        updates["applied_date"] = date.today().isoformat()

    if "status" not in document:
        updates["status"] = "Applied"

    if "job_url" not in document:
        updates["job_url"] = ""

    if "notes" not in document:
        updates["notes"] = ""

    if updates:
        applications.update_one(
            {"_id": document["_id"]},
            {"$set": updates},
        )

# mongoDB-side document validation rules
validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "company",
            "role",
            "status",
            "applied_date",
        ],
        "properties":{
            "company":{
                "bsonType": "string",
                "minLength": 1,
                "description": "Company name is required",
            },
            "role":{
                "bsonType": "string",
                "minLength": 1,
                "description": "job role is required",
            },
            "status": {
                "bsonType": "string",
                "enum": ALLOWED_STATUSES,
            },
            "applied_date":{
                "bsonType": "string",
                "pattern": r"^\d{4}-\d{2}-\d{2}$",
            },
            "job_url": {
                "bsonType": "string",
            },
            "notes": {
                "bsonType": "string",
            }
        }
    }
}
try:
    client_names = db.list_collection_names()

    if "applications" not in client_names:
        db.create_collection(
            "applications",
            validator=validator,
            validationLevel="strict",
            validationAction="error",
        )
    else:
        db.command({
            "collMod": "applications",
            "validator": validator,
            "validationLevel": "strict",
            "validationAction": "error",
        })

    print("MongoDB schema validation enabled!")
    print("Existing documents:", applications.count_documents({}))

except PyMongoError as error:
    print("Could not configure schema validation:", error)
