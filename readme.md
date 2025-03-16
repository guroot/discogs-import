# 🎵 Discogs Importer

This script allows you to **import albums into Discogs** from a CSV file, ensuring that your collection is accurately transferred while avoiding duplicates.

## 🚀 Features
- Imports albums into **a specific Discogs collection folder**.
- Uses **Discogs release IDs** for **precise importing**.
- **Avoids duplicates** by checking if the album already exists.
- **Supports CSV input** via command-line arguments.
- Retrieves the **latest version of `discogs_client` from GitHub**.

---

## 🛠 Installation

### 1️⃣ Clone the Repository
```sh
git clone https://github.com/your-username/discogs_importer.git
cd discogs_importer
```

### 2️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

👉 **This will install the latest `discogs_client` from GitHub**, as well as `pandas` for CSV handling.

### 3️⃣ Set Up Configuration
1. **Create a `config.ini` file** in the project directory:
   
   ```ini
   [Discogs]
   user_agent = DiscogsImporter/1.0
   token = YOUR_DISCOGS_TOKEN_HERE
   username = YOUR_USER_NAME_HERE
   collection_folder = YOUR_FOLDER_HERE
   ```

2. **Replace `YOUR_DISCOGS_TOKEN_HERE` `YOUR_USER_NAME_HERE` `YOUR_FOLDER_HERE`** with your **own information**.
   - You can generate an API token on [Discogs Developer Portal](https://www.discogs.com/settings/developers).

---

## 🎯 Usage

### **1️⃣ Import from the Default CSV File**
```sh
python discogs_importer.py
```
👉 This will **use `discogs_export.csv` by default**.

### **2️⃣ Import from a Custom CSV File**
```sh
python discogs_importer.py my_collection.csv
```
👉 Replace `my_collection.csv` with your own CSV export.

### **3️⃣ View Help Message**
```sh
python discogs_importer.py --help
```
👉 Displays:
```
usage: discogs_importer.py [csv_file]

Import albums into Discogs from a CSV file.

positional arguments:
  csv_file   Path to the CSV file (default: discogs_export.csv)
```

---

## 📝 CSV Format
The script requires a CSV file with at least the following columns:

| Column Name    | Description                           |
|---------------|---------------------------------------|
| `release_id`  | Unique ID of the Discogs release     |
| `Label`       | Label of the album                   |
| `Title`       | (Optional) Album title for reference |

Example CSV content:
```
release_id,Label,Title
123456,Blue Note,Kind of Blue
789012,Columbia,The Wall
```

---



## 👨‍💻 Contribution
Feel free to submit **pull requests** or open an **issue** if you find bugs or want to suggest improvements. 🎵

---

## 📝 License
This project is open-source under the **MIT License**.

---

## 🤝 Credits
- **Discogs API** - [Discogs Developer Portal](https://www.discogs.com/developers/)
- **Python Libraries** - `discogs_client`, `pandas`
- **Developed by:** Jonathan Fleury ---(https://github.com/guroot)

---

## 🎶 Happy Collecting!

