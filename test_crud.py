from pprint import pprint

from database import(
    client,
    applications,
    add_application,
    get_applications,
    get_application_by_id,
    update_application,
    validate_application,
    delete_application,
    delete_all_application
)

from pymongo.errors import PyMongoError

def main():
    try:
        client.admin.command("ping")
        print("Connected to MongoDB Atlas!\n")

        sample_data = [
        {
            "company": "Google",
            "role": "Backend Intern",
            "status": "Applied",
            "applied_date": "2025-09-15",
            "job_url": "https://careers.google.com/jobs/backend-intern",
            "notes": "Applied through Google Careers portal."
        },
        {
            "company": "Amazon",
            "role": "SDE Intern",
            "status": "Interview",
            "applied_date": "2025-09-10",
            "job_url": "https://amazon.jobs/sde-intern",
            "notes": "Passed online assessment. Interview scheduled."
        },
        {
            "company": "Microsoft",
            "role": "Software Intern",
            "status": "Applied",
            "applied_date": "2025-09-18",
            "job_url": "https://careers.microsoft.com/software-intern",
            "notes": "Applied via referral."
        },
        {
            "company": "Google",
            "role": "Graduate Engineer",
            "status": "Rejected",
            "applied_date": "2025-08-25",
            "job_url": "https://careers.google.com/jobs/graduate-engineer",
            "notes": "Rejected after first round interview."
        },
        {
            "company": "Adobe",
            "role": "Python Intern",
            "status": "Offer",
            "applied_date": "2025-09-05",
            "job_url": "https://careers.adobe.com/python-intern",
            "notes": "Offer received. Waiting to accept."
        }
        ]

        applications.insert_many(sample_data)

       # CREATE
        # print("1. CREATE")
        # application_id = add_application({
        #     "company": "Google",
        #     "role": "Software Engineer Intern",
        #     "status": "Applied",
        #     "job_url": "https://careers.google.com/",
        #     "notes": "Sample record for CRUD testing"
        # })
        # print("Inserted ID:", application_id)

        # # READ ONE
        # print("\n2. READ ONE")
        # record = get_application_by_id(str(application_id))
        # pprint(record)

        # # READ ALL
        # print("\n3. READ ALL")
        # for item in get_applications():
        #     pprint(item)

        # # UPDATE
        # print("\n4. UPDATE")
        # updated = update_application(
        #     str(application_id),
        #     {
        #         "status": "Interview",
        #         "notes": "Interview scheduled"
        #     }
        # )
        # print("Updated successfully:", updated)

        # print("Updated record:")
        # pprint(get_application_by_id(str(application_id)))

        # # VALIDATION TEST
        # print("\n5. VALIDATION TEST")
        # try:
        #     validate_application({
        #         "company": "",
        #         "role": "Backend Intern",
        #         "status": "Waiting"
        #     })
        # except ValueError as error:
        #     print("Invalid data rejected:", error)

        # # DELETE
        # print("\n6. DELETE")
        # deleted = delete_application(str(application_id))
        # print("Deleted successfully:", deleted)

        # # Verify deletion
        # print(
        #     "Record after deletion:",
        #     get_application_by_id(str(application_id))
        # )

        # print("\nCRUD demonstration completed!")

    except PyMongoError as error:
        print("MongoDB error:", error)

    except ValueError as error:
        print("Validation or input error:", error)

    finally:
        client.close()


if __name__ == "__main__":
    main()
 