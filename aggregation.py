from database import applications

def get_total_applications():
    return applications.count_documents({})

def get_status_summary():
    pipeline=[
        {
            "$group": {
                "_id": "$status",
                "total": {"$sum": 1}
            }

        },
        {
            "$sort": {"total": -1}
        }
    ]

    return list(applications.aggregate(pipeline))

def get_company_summary():
    pipeline = [
        {
            "$group": {
                "_id": "$company",
                "total": {"$sum": 1}
            }
        },
        {
            "$sort": {"total": -1, "_id": 1}
        }
    ]
    return list(applications.aggregate(pipeline))


def get_monthly_summary():
    """Count applications by month using YYYY-MM."""
    pipeline = [
        {
            "$match": {
                "applied_date": {
                    "$type": "string",
                    "$regex": r"^\d{4}-\d{2}-\d{2}$"
                }
            }
        },
        {
            "$project": {
                "month": {
                    "$substrBytes": ["$applied_date", 0, 7]
                }
            }
        },
        {
            "$group": {
                "_id": "$month",
                "total": {"$sum": 1}
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ]

    return list(applications.aggregate(pipeline))

    


def get_offer_count():
    """Count applications that resulted in an offer."""
    return applications.count_documents({"status": "Offer"})
    