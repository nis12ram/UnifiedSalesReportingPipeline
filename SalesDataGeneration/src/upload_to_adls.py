import os
from dotenv import load_dotenv
from azure.storage.filedatalake import DataLakeServiceClient


def get_service_client_sas(
    storage_account_name: str, storage_sas_token: str
) -> DataLakeServiceClient:
    account_url = f"https://{storage_account_name}.dfs.core.windows.net"
    service_client = DataLakeServiceClient(account_url, credential=storage_sas_token)
    return service_client


def upload_to_adls(
    service_client: DataLakeServiceClient,
    container_name: str,
    landing_directory_path: str,
    landing_file_name: str,
    local_data_path: str,
) -> None:
    fs_client = service_client.get_file_system_client(file_system=container_name)
    directory_client = fs_client.get_directory_client(landing_directory_path)
    file_client = directory_client.create_file(landing_file_name)
    with open(local_data_path, "rb") as data:
        file_client.upload_data(data, overwrite=True)



