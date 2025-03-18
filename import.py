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

# ✅ Global cache to avoid repeated API calls
COLLECTION_CACHE = {}

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




def load_collection_releases(folder_id):
    """
    Loads all releases from a collection folder and caches them.
    Handles API pagination correctly to avoid out-of-range errors.

    Args:
        folder_id (int): The ID of the collection folder.

    Returns:
        set: A set of release IDs in the specified folder.
    """
    global COLLECTION_CACHE

    # Return cached data if already loaded
    if folder_id in COLLECTION_CACHE:
        return COLLECTION_CACHE[folder_id]

    try:
        user = d.user(USERNAME)
        folder = user.collection_folders[folder_id]
        all_releases = set()  # Using a set for fast lookup (O(1) complexity)

        # ✅ Initialize pagination
        page = 1
        total_pages = 1  # Default to 1 (will be updated after first request)

        while page <= total_pages:
            releases = folder.releases.page(page)  # API paginated request

            if not releases:
                break  # Stop if no releases are returned

            # ✅ Get total number of pages from the first requesreleases.pagest
            if page == 1:
                total_pages = folder.releases.pages  # Discogs API provides total pages

            # Add all release IDs from the current page
            all_releases.update(release.release.id for release in releases)
            page += 1  # Move to the next pagereleases.pages

        # Store results in cache
        COLLECTION_CACHE[folder_id] = all_releases
        return all_releases

    except Exception as e:
        print(f"❌ Error loading collection: {e}")
        return set()  # Return an empty set in case of an error


def is_already_in_collection(release_id, folder_id):
    """
    Checks if a release is already present in the collection using cached data.

    Args:
        release_id (int): The ID of the release to check.
        folder_id (int): The ID of the collection folder.

    Returns:
        bool: True if the release is in the collection, False otherwise.
    """
    collection_releases = load_collection_releases(folder_id)
    return release_id in collection_releases  # Fast O(1) lookup


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
