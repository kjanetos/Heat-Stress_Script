import os

from azure.storage.blob import ContainerClient

from pipeline.config_loader import load_config


# ============================================================
# Load Config
# ============================================================

config = load_config()

ACCOUNT_NAME = config["ACCOUNT_NAME"]
TEMP_CONTAINER_NAME = config["TEMP_CONTAINER_NAME"]
SAS_TOKEN = config["TEMP_SAS_TOKEN"]


# ============================================================
# Azure Connection
# ============================================================

container = ContainerClient(
    account_url=f"https://{ACCOUNT_NAME}.blob.core.windows.net",
    container_name=TEMP_CONTAINER_NAME,
    credential=SAS_TOKEN
)


# ============================================================
# Find Raw TEMP
# ============================================================

def find_raw_temp(pid, day):

    print("\nSearching Azure...")
    print(f"PID : {pid}")
    print(f"Day : D{day}")

    raw_blob = None

    try:

        for blob in container.list_blobs(
            name_starts_with="DOSE/"
        ):

            path = blob.name.replace("\\", "/")

            # PID
            if pid.lower() not in path.lower():
                continue

            # Day
            if f"/D{day}/".lower() not in path.lower():
                continue

            # TEMP folder
            if "/temp/" not in path.lower():
                continue

            # Filename
            filename = os.path.basename(path)

            # Exclude preview
            if "preview" in filename.lower():
                continue

            print("\nFOUND RAW TEMP:")
            print(path)

            raw_blob = blob
            break

    except Exception as e:

        print("\nAzure Error while searching:")
        print(type(e).__name__)
        print(e)

        return None

    if raw_blob is None:

        print("\nNo Raw TEMP file found in Azure.")

        return None

    return raw_blob


# ============================================================
# Download Raw TEMP
# ============================================================

def download_raw_temp(raw_blob, download_folder):

    if not download_folder:
        return None

    local_file = os.path.join(
        download_folder,
        os.path.basename(raw_blob.name)
    )

    print("\nDownloading:")
    print(raw_blob.name)

    print("\nSaving to:")
    print(local_file)

    try:

        with open(local_file, "wb") as f:

            data = container.download_blob(
                raw_blob.name
            )

            f.write(
                data.readall()
            )

    except Exception as e:

        print("\nAzure Download Error:")
        print(type(e).__name__)
        print(e)

        return None

    print("\nDownload Complete.")

    return local_file