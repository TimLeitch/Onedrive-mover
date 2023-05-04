
# OneDrive Mover

This script allows you to move OneDrive items from one user to a specific folder in another user's OneDrive. It provides a simple GUI to select the source user, destination folder, and also create new folders if needed.

## Prerequisites

To use this script, you need:

1. Python 3 installed on your system
2. The following Python packages installed:

   - `tkinter`
   - `requests`
   - `python-dotenv`

You can install these packages with the following command:

```sh
pip install tk requests python-dotenv
```

3. An Azure Active Directory application with the `Microsoft Graph API` and appropriate permissions.
4. A `.env` file in the same directory as the script containing the following values:

```
CLIENT_ID=<your_client_id>
CLIENT_SECRET=<your_client_secret>
TENANT_ID=<your_tenant_id>
BASE_URI=https://graph.microsoft.com/v1.0
```

Replace `<your_client_id>`, `<your_client_secret>`, and `<your_tenant_id>` with your actual Azure AD application values.

## Usage

To run the script, open a terminal or command prompt, navigate to the directory where the script is located, and run:

```sh
python OneDrive_Mover.py
```

The script will open a GUI window. Follow these steps to move items from one user's OneDrive to another user's OneDrive:

1. Select the source user from the "Select User" dropdown.
2. Select the destination folder from the "Select or Create Folder" dropdown or create a new folder by typing the folder name in the "Folder Name" input box and clicking the "Create Folder" button.
3. Click the "Refresh" button to update the users and folders list (if needed after creating a new folder).
4. Click the "Start Move" button to initiate the move process.

## Note

This script moves items from one user's OneDrive to a specific folder in another user's OneDrive. It does not handle permissions, sharing settings, or other metadata. Please use this script with caution and ensure you have proper backups before running it on any production environment.
The current destination user is hard coded in the script. You will need to modify this to suit your needs.

The script has been tested with Python 3.8+ on Windows 10. Your mileage may vary on other platforms or Python versions.


##TODO
- [ ] Add support for moving files from a specific folder in the source user's OneDrive
- [ ] Add support for moving files to a specific folder in the destination user's OneDrive
- [ ] Add support for selecting the destination user from a dropdown, or at the least, make the destination user configurable
