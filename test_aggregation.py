
from pprint import pprint

from database import client
from aggregation import (
    get_total_applications,
    get_status_summary,
    get_company_summary,
    get_monthly_summary,
    get_offer_count
)

try:
    client.admin.command("ping")

    print("\n--- TOTAL APPLICATIONS ---")
    print(get_total_applications())

    print("\n--- APPLICATIONS BY STATUS ---")
    pprint(get_status_summary())

    print("\n--- APPLICATIONS BY COMPANY ---")
    pprint(get_company_summary())

    print("\n--- APPLICATIONS BY MONTH ---")
    pprint(get_monthly_summary())

    print("\n--- TOTAL OFFERS ---")
    print(get_offer_count())

except Exception as error:
    print("Error:", error)

finally:
    client.close()
