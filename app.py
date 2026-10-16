import streamlit as st
import pandas as pd

from datetime import date

from database import(
    applications,
    add_application,
    get_applications,
    get_application_by_id,
    update_application,
    validate_application,
    delete_application,
    delete_all_application
)

from aggregation import (
    get_total_applications,
    get_status_summary,
    get_company_summary,
    get_monthly_summary,
    get_offer_count
)

st.set_page_config(
    page_title="Job Application Tracker",
    page_icon="💼",
    layout="wide",
)

st.title("Job Application Tracker")
st.caption("Manage your job applications, interviews, and offers in one place.")

STATUSES = [
    "Applied",
    "Online Assessment",
    "Interview",
    "Offer",
    "Rejected"
]

## Dashboard metrics

try: 
    total = get_total_applications()
    status_data = get_status_summary()
    offers = get_offer_count()
    interview_count = sum(
        item["total"]
        for item in status_data
        if item["_id"] == "Interview"
    )

    assessment_count = sum(
        item["total"]
        for item in status_data
        if item["_id"] == "Online Assessment"
    )

except Exception as error:
    st.error(f"Could not load dashboard metrics: {error}")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Applications", total)
col2.metric("Interviews", interview_count)
col3.metric("Online Assessments", assessment_count)
col4.metric("Offers", offers)

st.divider()

# Add application form

st.header("Add a New Application")

with st.form("add_application_form", clear_on_submit=True):
    company = st.text_input("Company Name")
    role = st.text_input("Job Role")

    col1, col2 = st.columns(2)
    with col1:
        status = st.selectbox("Application Status", STATUSES)
        applied_date = st.date_input(
            "Applied Date",
            value=date.today(),
            max_value=date.today()
        )

    with col2:
        job_url = st.text_input("Job Posting URL(optional)")
        notes = st.text_area("Notes (optional)")

    submitted = st.form_submit_button(
        "Add Application",
        type="primary"
    )
    if submitted:
        try: 
            application_id = add_application({
                "company": company,
                "role": role,
                "status": status,
                "applied_date": applied_date.isoformat(),
                "job_url": job_url,
                "notes": notes
            })
            st.success(
                f"Application added successfully! ID: {application_id}"
            )
            st.rerun()
        except ValueError as error:
            st.error(f"Invalid data: {error}")
        except Exception as error:
            st.error(f"Could not add application: {error}")

st.divider()

#view and filter applications
st.header("Your Applications")

try:
    records = get_applications()

except Exception as error:
    st.error(f"Could not load applications: {error}")
    st.stop()

search = st.text_input("Search by company or role")

filter_status = st.selectbox(
    "Filter by status",
    ["All"] + STATUSES,
)

filtered_records = []

for record in records:
    company_name = record.get("company", "").lower()
    role_name = record.get("role", "").lower()
    record_status = record.get("status", "")

    matches_search = (
        search.lower() in company_name or
        search.lower() in role_name
    )

    matches_status = (
        filter_status == "All" or
        record_status == filter_status
    )

    if matches_search and matches_status:
        filtered_records.append(record)

if filtered_records:
    display_records = []

    for record in filtered_records:
        display_records.append({
            "ID": str(record["_id"]),
            "Company": record.get("company", ""),
            "Role": record.get("role", ""),
            "Status": record.get("status", ""),
            "Applied Date": record.get("applied_date", ""),
            "Job URL": record.get("job_url", ""),
            "Notes": record.get("notes", "")
        })
    st.dataframe(
        pd.DataFrame(display_records),
        use_container_width=True,
        hide_index=True,
    )
else: 
    st.info("No applications found matching the criteria.")

st.caption(f"Showing {len(filtered_records)} of {len(records)} total applications.")
st.divider()

#edit application

st.header("Edit an Application")
if records: 
    record_map = {
        str(record["_id"]): record
        for record in records
    }
    selected_id = st.selectbox(
        "select an application to edit",
        options=list(record_map.keys()),
        format_func= lambda app_id: (
            f"{record_map[app_id].get('company', 'Unknown')} - "
            f"{record_map[app_id].get('role', 'Unknown')}"
            f"({record_map[app_id].get('status', 'Unknown')})"
        ),
        key="edit_application_id",
    )
    selected_record = record_map[selected_id]

    with st.form("edit_application_form"):
        edit_company = st.text_input(
            "Company Name",
            value=selected_record.get("company", ""),
        )
        edit_role = st.text_input(
            "Job Role",
            value=selected_record.get("role", ""),
        )

        current_status = selected_record.get("status", "Applied")
        edit_status = st.selectbox(
            "Status",
            STATUSES,
            index=(
                STATUSES.index(current_status)
                if current_status in STATUSES
                else 0
            ),
        )
        existing_date = selected_record.get(
            "applied_date",
            date.today().isoformat()
        )

        try:
            parsed_date = date.fromisoformat(existing_date)
            if parsed_date > date.today():
                parsed_date = date.today()
        except (ValueError, TypeError):
            parsed_date = date.today()

        edit_date = st.date_input(
            "Application Date",
            value=parsed_date,
            max_value=date.today(),
        )

        edit_url = st.text_input(
            "Job URL",
            value=selected_record.get("job_url", ""),
        )

        edit_notes = st.text_area(
            "Notes",
            value=selected_record.get("notes", ""),
        )

        save_changes = st.form_submit_button(
            "Save Changes",
            type="primary",
        )

        if save_changes:
            try:
                updated = update_application(
                    selected_id,
                    {
                        "company": edit_company,
                        "role": edit_role,
                        "status": edit_status,
                        "applied_date": edit_date.isoformat(),
                        "job_url": edit_url,
                        "notes": edit_notes,
                    },
                )

                if updated:
                    st.success("Application updated successfully!")
                else:
                    st.info(
                        "No changes made, or the application no longer exists."
                    )

                st.rerun()

            except ValueError as error:
                st.error(str(error))

            except Exception as error:
                st.error(f"Could not update application: {error}")

else:
    st.info("Add an application before using the edit feature.")


st.divider()


# delete application
st.header("Delete an Application")

if records:
    delete_id = st.selectbox(
        "Choose an application to delete",
        options=list(record_map.keys()),
        format_func=lambda app_id: (
            f"{record_map[app_id].get('company', 'Unknown')} - "
            f"{record_map[app_id].get('role', 'Unknown')}"
            f"({record_map[app_id].get('status', 'Unknown')})"
        ),
        key="delete_application_id",
    )
    confirm_delete = st.checkbox(
        "I understand that this action cannot be undone."
    )
    if st.button("Delete Application", type="secondary"):
        if not confirm_delete:
            st.warning("Please confirm deletion by checking the box.")
        else:
            try:
                deleted = delete_application(delete_id)
                if deleted:
                    st.success("Application deleted successfully.")
                else:
                    st.info("The application no longer exists.")

                st.rerun()
            except Exception as error:
                st.error(f"Could not delete application: {error}")

else:
    st.info("Select an application to delete.")

st.divider()


#analytics and summaries

st.header("Application Analytics")
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("Applications by Status")

    if status_data:
        status_df = pd.DataFrame([
            {
                "Status": item["_id"],
                "Applications": item["total"]
            
            }
            for item in status_data
        ])

        st.bar_chart(
            status_df.set_index("Status"),
        )
    else:
        st.info("No applications found to display status summary.")

with col3:
    st.subheader("Applications by Company")

    try:
        company_data = get_company_summary()
        if company_data:
            company_df = pd.DataFrame([
                {
                    "Company": item["_id"],
                    "Applications": item["total"]
                }
                for item in company_data
            ])
            st.bar_chart(
                company_df.set_index("Company"),
            )
        else:
            st.info("Add applications to see the company summary.")
    except Exception as error:
        st.error(f"Could not load company summary: {error}")

st.divider()

# delete all applications at once

st.header("Delete All Applications")
confirm_delete_all = st.checkbox(
    "I understand that this action will delete all applications and cannot be undone."
    )

try:
    if st.button("Delete All Applications", type="secondary"):
        if not confirm_delete_all:
            st.warning("Please confirm deletion by checking the box.")
        else:
            deleted_count = delete_all_application()
            if deleted_count:
                st.success(f"Deleted {deleted_count} applications successfully.")
            else:
                st.info("There are no applications to delete.")
            st.stop()
except Exception as error:
    st.error(f"Could not delete all applications: {error}")

