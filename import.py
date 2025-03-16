import discogs_client
import pandas as pd
import csv
import time
import configparser
import argparse
import os

# ✅ Load configuration from config.ini
config = configparser.ConfigParser()
config.read("config.ini")

DISCOGS_USER_AGENT = config.get("Discogs", "user_agent")
DISCOGS_TOKEN = config.get("Discogs", "token")
USERNAME = config.get("Discogs", "username")
COLLECTION_FOLDER_NAME = config.get("Discogs", "collection_folder")

# ✅ Global variable to avoid repeated API calls
FOLDER_INDEX_CACHE = None

# Initialize the Discogs client
d = discogs_client.Client(DISCOGS_USER_AGENT, user_token=DISCOGS_TOKEN)

# Function to retrieve the index of the collection folder only once
def get_folder_index(folder_name):
    global FOLDER_INDEX_CACHE
    if FOLDER_INDEX_CACHE is not None:
        return FOLDER_INDEX_CACHE  # Return cached index

    try:
        user = d.user(USERNAME)
        folders = list(user.collection_folders)  # Convert to explicit list

        print("📂 Available collection folders:")
        for i, folder in enumerate(folders):
            print(f"  [{i}] - {folder.name} (ID: {folder.id})")  # Debugging

        for i, folder in enumerate(folders):
            if folder.name.lower() == folder_name.lower():
                print(f"📂 Folder found: {folder.name} (Index: {i}, ID: {folder.id})")
                FOLDER_INDEX_CACHE = i  # Cache the index
                return FOLDER_INDEX_CACHE

        print(f"⚠️ Folder '{folder_name}' not found. Using 'Uncategorized'.")
        FOLDER_INDEX_CACHE = 0  # Default to index 0 (Uncategorized)
        return FOLDER_INDEX_CACHE

    except Exception as e:
        print(f"❌ Error retrieving folder: {e}")
        FOLDER_INDEX_CACHE = 0  # Default to Uncategorized
        return FOLDER_INDEX_CACHE

# Function to check if a release is already in the collection
def is_already_in_collection(release_id, folder_id):
    try:
        user = d.user(USERNAME)
        folder = user.collection_folders[folder_id]

        # Iterate through releases in the folder to check for duplicates
        for item in folder.releases:
            if item.release.id == release_id:
                print(f"🔄 The album {item.release.title} ({item.release.year}) is already in the collection.")
                return True  # Release already exists

        return False  # Not found, can be added

    except Exception as e:
        print(f"❌ Error checking existing releases: {e}")
        return False

# Function to add an album to the collection
def add_to_collection(release_id, folder_id):
    try:
        release = d.release(release_id)
        print(f"Adding {release.title} ({release.year}) to '{COLLECTION_FOLDER_NAME}'...")

        user = d.user(USERNAME)

        # ✅ Check if release is already in the collection
        if is_already_in_collection(release.id, folder_id):
            print(f"✅ {release.title} ({release.year}) is already in the collection, skipping.")
            return False

        print(f"📂 Adding to collection_folders[{folder_id}]...")  # Debugging

        # ✅ Add album to the specified folder
        me = d.identity()
        me.collection_folders[folder_id].add_release(release.id)

        print(f"✅ Added: {release.title} ({release.year})")
        time.sleep(4)  # Pause to avoid API rate limits
        return True
    except Exception as e:
        print(f"❌ Error adding {release_id}: {e}")
        return False

# Function to import a CSV file using release_id
def import_csv_to_discogs(csv_file):
    # ✅ Check if file exists before proceeding
    if not os.path.isfile(csv_file):
        print(f"❌ Error: CSV file '{csv_file}' not found.")
        return

    df = pd.read_csv(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)

    # Retrieve the folder ID for the collection folder
    folder_id = get_folder_index(COLLECTION_FOLDER_NAME)

    total = len(df)
    success = 0

    for _, row in df.iterrows():
        release_id = row.get("release_id", "")
        label = row.get("Label", "").strip()

        if not release_id or not label:
            print(f"⚠️ Missing Catalog# or Label for {row.get('Title', 'Unknown')}, skipped.")
            continue

        if release_id:
            if add_to_collection(int(release_id), folder_id):
                success += 1

    print(f"\n✅ Import completed: {success}/{total} albums added to '{COLLECTION_FOLDER_NAME}'.")

# ✅ Command-line argument parser
def main():
    parser = argparse.ArgumentParser(description="Import albums into Discogs from a CSV file.")
    parser.add_argument("csv_file", nargs="?", default="discogs_export.csv", help="Path to the CSV file (default: discogs_export.csv)")
    args = parser.parse_args()

    # Start the import process
    import_csv_to_discogs(args.csv_file)

if __name__ == "__main__":
    main()
