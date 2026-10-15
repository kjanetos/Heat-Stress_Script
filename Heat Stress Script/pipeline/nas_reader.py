import os

import stat

import paramiko
 
from pipeline.config_loader import load_config
 
 
# ============================================================

# Load Config

# ============================================================
 
config = load_config()
 
SFTP_HOST = config["SFTP_HOST"]

SFTP_PORT = int(config["SFTP_PORT"])

SFTP_USERNAME = config["SFTP_USERNAME"]

SFTP_PASSWORD = config["SFTP_PASSWORD"]
 
TEMP_ROOT_PREFIX = config.get(

    "TEMP_ROOT_PREFIX",

    "CISWP/operations/DOSE/"

)
 
RAW_TEMP_FOLDER = config.get(

    "RAW_TEMP_FOLDER",

    "TEMP"

)
 
IGNORE_FILE = config.get(

    "IGNORE_FILE",

    "PREVIEW"

)
 
 
# ============================================================

# SFTP Connection

# ============================================================
 
def connect_sftp():
 
    print("\nConnecting to SFTP...")
 
    transport = paramiko.Transport(

        (SFTP_HOST, SFTP_PORT)

    )
 
    transport.connect(

        username=SFTP_USERNAME,

        password=SFTP_PASSWORD

    )
 
    sftp = paramiko.SFTPClient.from_transport(

        transport

    )
 
    print("SFTP connection successful.")
 
    return sftp, transport
 
 
# ============================================================

# Find TEMP Folder Recursively

# ============================================================
 
def find_temp_folder(sftp, current_path, pid, day):
 
    try:

        items = sftp.listdir_attr(current_path)
 
    except Exception:

        return None
 
    for item in items:
 
        item_name = item.filename

        item_path = f"{current_path}/{item_name}"
 
        # ----------------------------------------------------

        # Only search directories

        # ----------------------------------------------------
 
        if not stat.S_ISDIR(item.st_mode):

            continue
 
        # ----------------------------------------------------

        # Ignore hidden/system folders if needed

        # ----------------------------------------------------
 
        if item_name.startswith("."):

            continue
 
        # ----------------------------------------------------

        # Check for TEMP folder

        # ----------------------------------------------------
 
        if item_name.lower() == RAW_TEMP_FOLDER.lower():
 
            # TEMP folder must be inside the requested

            # participant/day area.

            #

            # We verify the path contains the PID and

            # the appropriate Day folder somewhere above it.
 
            path_lower = item_path.lower()
 
            pid_lower = pid.lower()
 
            day_folder_1 = f"{pid}_D{day}".lower()

            day_folder_2 = f"D{day}".lower()
 
            if (

                pid_lower in path_lower

                and (

                    day_folder_1 in path_lower

                    or day_folder_2 in path_lower

                )

            ):
 
                return item_path
 
        # ----------------------------------------------------

        # Continue searching subfolders

        # ----------------------------------------------------
 
        result = find_temp_folder(

            sftp,

            item_path,

            pid,

            day

        )
 
        if result is not None:

            return result
 
    return None
 
 
# ============================================================

# Find Raw TEMP

# ============================================================
 
def find_raw_temp(pid, day):
 
    sftp = None

    transport = None
 
    try:
 
        sftp, transport = connect_sftp()
 
        print("\nSearching SFTP...")

        print(f"PID : {pid}")

        print(f"Day : D{day}")
 
        print("\nStarting search from:")

        print(TEMP_ROOT_PREFIX)
 
        # ----------------------------------------------------

        # Find TEMP folder

        # ----------------------------------------------------
 
        temp_folder = find_temp_folder(

            sftp,

            TEMP_ROOT_PREFIX.rstrip("/"),

            pid,

            day

        )
 
        if temp_folder is None:
 
            print("\nNo matching TEMP folder found on SFTP.")
 
            return None
 
        print("\nFOUND TEMP FOLDER:")

        print(temp_folder)
 
        # ----------------------------------------------------

        # Find Raw TEMP file

        # ----------------------------------------------------
 
        files = sftp.listdir_attr(

            temp_folder

        )
 
        for item in files:
 
            filename = item.filename
 
            # Skip directories

            if stat.S_ISDIR(item.st_mode):

                continue
 
            # Skip preview files

            if IGNORE_FILE.lower() in filename.lower():

                continue
 
            remote_path = (

                f"{temp_folder}/{filename}"

            )
 
            print("\nFOUND RAW TEMP:")

            print(remote_path)
 
            return remote_path
 
        print("\nTEMP folder found, but no Raw TEMP file was found.")
 
        return None
 
    except Exception as e:
 
        print("\nSFTP Error while searching:")

        print(type(e).__name__)

        print(e)
 
        return None
 
    finally:
 
        if sftp is not None:

            sftp.close()
 
        if transport is not None:

            transport.close()
 
 
# ============================================================

# Download Raw TEMP

# ============================================================
 
def download_raw_temp(remote_path, download_folder):
 
    if not remote_path:

        return None
 
    if not download_folder:

        return None
 
    sftp = None

    transport = None
 
    try:
 
        sftp, transport = connect_sftp()
 
        filename = os.path.basename(

            remote_path

        )
 
        local_file = os.path.join(

            download_folder,

            filename

        )
 
        print("\nDownloading Raw TEMP:")

        print(remote_path)
 
        print("\nSaving to:")

        print(local_file)
 
        sftp.get(

            remote_path,

            local_file

        )
 
        print("\nDownload Complete.")

        print("Local file:")

        print(local_file)
 
        return local_file
 
    except Exception as e:
 
        print("\nSFTP Download Error:")

        print(type(e).__name__)

        print(e)
 
        return None
 
    finally:
 
        if sftp is not None:

            sftp.close()
 
        if transport is not None:

            transport.close()
 