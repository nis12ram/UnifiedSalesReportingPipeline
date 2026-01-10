import os
from dotenv import load_dotenv
from generate_realistic_sales_files import generate_data
from upload_to_adls import get_service_client_sas, upload_to_adls

load_dotenv()
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME")
SHARED_CONTAINER_NAME = os.getenv("SHARED_CONTAINER_NAME")
NORTH_DIRECTORY_SAS_TOKEN = os.getenv("STORAGE_SAS_TOKEN")
SOUTH_DIRECTORY_SAS_TOKEN = os.getenv("STORAGE_SAS_TOKEN")
WEST_DIRECTORY_SAS_TOKEN = os.getenv("STORAGE_SAS_TOKEN")

root_path = r"D:\test_locally_notebooks\automated_trusted_daily_sales_reporting_across_distributed_branches\realistic_sales_data"

service_client_for_north = get_service_client_sas(
    STORAGE_ACCOUNT_NAME, NORTH_DIRECTORY_SAS_TOKEN
)
service_client_for_south = get_service_client_sas(
    STORAGE_ACCOUNT_NAME, SOUTH_DIRECTORY_SAS_TOKEN
)
service_client_for_west = get_service_client_sas(
    STORAGE_ACCOUNT_NAME, WEST_DIRECTORY_SAS_TOKEN
)
regional_branches_service_client = {
    "north": service_client_for_north,
    "south": service_client_for_south,
    "west": service_client_for_west,
}


def main(just_generate: bool = False):
    manifest = generate_data(root_path=root_path)
    print(f"manifest: {manifest}")
    if just_generate:
        return None
    for regional_branch, service_client in regional_branches_service_client.items():
        upload_to_adls(
            service_client=service_client,
            container_name=SHARED_CONTAINER_NAME,
            landing_directory_path=regional_branch,
            landing_file_name=manifest["files_name"][regional_branch],
            local_data_path=manifest["files_path"][regional_branch],
        )
    print("Sales data uploaded successfully")


if __name__ == "__main__":
    main(just_generate=False)
