import os

from azure.storage.blob import ContainerClient

from pipeline.config_loader import load_config


# ============================================================
# Load Config
# ============================================================

config = load_config()

ACCOUNT_NAME = config["ACCOUNT_NAME"]
HR_CONTAINER_NAME = config["HR_CONTAINER_NAME"]
HR_SAS_TOKEN = config["HR_SAS_TOKEN"]


# ============================================================
# Azure HR Connection
# ============================================================

container = ContainerClient(
    account_url=f"https://{ACCOUNT_NAME}.blob.core.windows.net",
    container_name=HR_CONTAINER_NAME,
    credential=HR_SAS_TOKEN
)


# ============================================================
# Find HR File
# ============================================================

def find_hr_file(pid, day):

    target_prefix = f"DoseData/{pid}/{pid}_D{day}/HR/"

    print("\nSearching Azure HR...")
    print("PID :", pid)
    print("Day : D" + str(day))
    print("Container :", HR_CONTAINER_NAME)
    print("Prefix :", target_prefix)

    for blob in container.list_blobs(
        name_starts_with=target_prefix
    ):

        path = blob.name.replace("\\", "/")
        filename = os.path.basename(path)

        # Skip PerWnd files
        if "PerWnd" in filename:
            continue

        # Only Excel files
        if not filename.lower().endswith(".xlsx"):
            continue

        print("\nFOUND ORIGINAL HR FILE:")
        print(path)

        return blob

    print("\nNo original HR file found.")

    return None
# ============================================================
# Download HR File
# ============================================================

def download_hr_file(blob, download_folder):

    if blob is None:
        return None

    filename = os.path.basename(blob.name)

    local_file = os.path.join(
        download_folder,
        filename
    )

    print("\nDownloading HR:")
    print(blob.name)

    print("\nSaving to:")
    print(local_file)

    with open(local_file, "wb") as f:

        data = container.download_blob(
            blob.name
        )

        f.write(data.readall())

    print("\nHR Download Complete.")

    return local_file