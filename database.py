import os
from datetime import date
from urllib.parse import urlparse

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

load_dotenv()
MONGO_URI = os.getenv("MONGO_URL")

if not MONGO_URI:
    raise ValueError("MONGO_URI is not avalible in .env file")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

db = client["job_tracker"]
applications = db['applications']

#allowed application statuses
ALLOWED_STATUSES = {
    "Applied",
    "Online Assesment",
    "Interview",
    "Offer",
    "Rejected"
}

# fields users are allowed to change
EDITABLE_FIELDS = {
    "company",
    "role",
    "status",
    "applied_date",
    "job_url",
    "notes"
}

def validate_application(data):
    """validate application data before writing to MongoDB"""
    if not isinstance(data, dict):
        raise ValueError("application data must be a dictionary")

    company = data.get("company")
    role = data.get("role")

    if not isinstance(company, str) or not company.strip():
        raise ValueError("Company name is required")

    if not isinstance(role, str) or not role.strip():
        raise ValueError("job role is required")

    status = data.get("status", "Applied")

    if status not in ALLOWED_STATUSES:
        raise ValueError(
            f"Status must be one of: {', '.join(sorted(ALLOWED_STATUSES))}"
        )

    applied_date = data.get("applied_date", date.today().isoformat())

    try:
        parsed_date = date.fromisoformat(applied_date)
    except(TypeError, ValueError):
        raise ValueError("Date must use YYYY-MM-DD format")

    if parsed_date > date.today():
        raise ValueError("Application date cannot be in the future")

    job_url = data.get("job_url", "")

    if not isinstance(job_url, str):
        raise ValueError("Job URL must be a text")

    if job_url:
        parsed_url = urlparse(job_url)
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise ValueError("Enter a valid HTTP or HTTPS job URL")


    notes = data.get("notes", "")
    if not isinstance(notes,  str):
        raise ValueError("Notes must be text")

    # return a clean document containing only expected fields.
    return {
        "company": company.strip(),
        "role": role.strip(),
        "status": status,
        "applied_date": applied_date,
        "job_url": job_url.strip(),
        "notes": notes.strip()
    }

# Create: add new applications
def add_application(data):
    document = validate_application(data)
    result = applications.insert_one(document)
    return result.inserted_id

# Read: Read all application GET
def get_applications():
    return list(
        applications.find().sort("applied_date", -1)
    )

# Read: Get one application by its MOngoDB id
def get_application_by_id(application_id):
    from bson import ObjectId
    if not ObjectId.is_valid(application_id):
        raise ValueError("Invalid application ID")
    return applications.find_one({
        "_id": ObjectId(application_id)
    })

#Update: update application by application id
def update_application(application_id, changes):
    from bson import ObjectId
    if not ObjectId.is_valid(application_id):
        raise ValueError("Invalid application ID")
    
    if not isinstance(changes, dict) or not changes:
        raise ValueError("Provide at least one field to update")

    Invalid_fields = set(changes) - EDITABLE_FIELDS

    if Invalid_fields:
        raise ValueError(
            f"Fields cannot be updated: {', '.join(sorted(Invalid_fields))}"

        )
    existing = get_application_by_id(application_id)

    if existing is None: 
        return False

    updated_document = {
        **{key: existing[key] for key in EDITABLE_FIELDS
           if key in existing},
        **changes

    }
    # validate the complete document
    validate_document = validate_application(updated_document)

    result = applications.update_one(
        {"_id": ObjectId(application_id)},
        {"$set": validate_document}
    )

    return result.modified_count > 0

#delete : remove one application

def delete_application(application_id):
    from bson import ObjectId
    if not ObjectId.is_valid(application_id):
        raise ValueError("Invalid application ID")

    result = applications.delete_one({
        "_id": ObjectId(application_id)
    })
    return result.deleted_count>0

#delete: remove all applications

def delete_all_application():
    result = applications.delete_many({})
    return result.deleted_count


    