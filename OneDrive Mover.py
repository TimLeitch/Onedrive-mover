import tkinter as tk
from tkinter import ttk
import requests
from dotenv import dotenv_values

config = dotenv_values('.env')

def get_token(): 
    uri = f"https://login.microsoftonline.com/{config['TENANT_ID']}/oauth2/v2.0/token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {
        'client_id': config['CLIENT_ID'],
        'scope': 'https://graph.microsoft.com/.default',
        'client_secret': config['CLIENT_SECRET'],
        'grant_type': 'client_credentials'
    }
    response = requests.post(uri, headers=headers, data=payload)
    response_json = response.json()

    if 'access_token' not in response_json:
        print("Error getting access token:", response_json)
        return None
    return response_json['access_token']

def get_users():
    access_token = get_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    url = config['BASE_URI'] + "/users?$top=999&$orderby=displayName"
    res = requests.get(url, headers=headers)
    return handle_pagination(res, headers)


def create_new_folder(folder_name):
    headers = {"Authorization": f"Bearer {get_token()}"}
    url = f'https://graph.microsoft.com/v1.0/users/ced1d981-4c26-42d8-af9b-475165161e93/drive/root/children'
    json = { "name": folder_name, "folder": {}, "@microsoft.graph.conflictBehavior": "rename" }
    response = requests.post(url, headers=headers, json=json)
    return response.json()
  
def get_user_drive(upn):
    headers = {"Authorization": f"Bearer {get_token()}"}
    url = f'https://graph.microsoft.com/v1.0/users/{upn}/drive'
    response = requests.get(url, headers=headers)
    return response.json() 

def get_items_in_drive(upn):
    headers = {"Authorization": f"Bearer {get_token()}"}
    url = f'https://graph.microsoft.com/v1.0/users/{upn}/drive/root/children'
    res = requests.get(url, headers=headers)
    return handle_pagination(res, headers)

def get_ee_folder_ids():
    headers = {"Authorization": f"Bearer {get_token()}"}
    url = f'https://graph.microsoft.com/v1.0/users/ced1d981-4c26-42d8-af9b-475165161e93/drive/root/children'
    res = requests.get(url, headers=headers)
    return handle_pagination(res, headers)

def handle_pagination(res, headers):
    data = res.json()['value']
    
    while '@odata.nextLink' in res.json():
        response = requests.get(res.json()['@odata.nextLink'], headers=headers)
        data.extend(response.json()['value'])
        res.json()['@odata.nextLink'] = response.json()['@odata.nextLink']
    
    return data


def check_if_folder_exists(folder_name):
    folders = get_ee_folder_ids()
    for folder in folders:
        if folder['name'] == folder_name:
            return folder['id']
    return None

def move_item_to_drive(upn, item_id, folder_name):
    headers = {"Authorization": f"Bearer {get_token()}"}
    url = f'https://graph.microsoft.com/v1.0/users/{upn}/drive/items/{item_id}/copy'
    json = {
            "parentReference": {
                "driveId": get_user_drive('ced1d981-4c26-42d8-af9b-475165161e93')['id'],
                "id": check_if_folder_exists(folder_name)
        }   
    }
    response = requests.post(url, headers=headers, json=json)
    print(response)     

def get_all_users():
    users = get_users()
    display_names_upns = {user['displayName']: user['userPrincipalName'] for user in users}
    return display_names_upns

def get_all_ee_folder_names():
    folders = get_ee_folder_ids()
    folder_names = [folder['name'] for folder in folders]
    return folder_names

def create_folder():
    folder_name = folder_name_var.get()
    folder_id = check_if_folder_exists(folder_name)
    if folder_id is None:
        response = create_new_folder(folder_name)
        print(f"Creating folder: {folder_name}")
        if 'error' in response:
            status_var.set(f"Error creating folder: {response['error']['message']}")
        else:
            status_var.set(f"Created folder: {folder_name}")
    else:
        status_var.set("Folder already exists")

def refresh():
    users_combobox.set('')  # Clear the current user selection
    users_combobox['values'] = list(get_all_users().keys())  # Update user values
    folders_combobox.set('')  # Clear the current folder selection
    folders_combobox['values'] = get_all_ee_folder_names()  # Update folder values
    status_var.set("Refreshed users and folders")

def start_move():
    selected_user_display_name = users_combobox.get()
    user_to_move_upn = users_upns_dict[selected_user_display_name]
    folder_name = folders_combobox.get()
    items = get_items_in_drive(user_to_move_upn)

    for item in items:
        move_item_to_drive(user_to_move_upn, item['id'], folder_name)

    status_var.set("Move initiated")

def close_app():
    root.destroy()

root = tk.Tk()
root.title("Move Items to EE Archive Mailbox")

user_label = tk.Label(root, text="Select User:")
users_upns_dict = get_all_users()
users_combobox = ttk.Combobox(root, values=list(users_upns_dict.keys()))

folder_label = tk.Label(root, text="Select or Create Folder:")
folders_combobox = ttk.Combobox(root, values=get_all_ee_folder_names())

folder_name_label = tk.Label(root, text="Folder Name:")
folder_name_var = tk.StringVar()
folder_name_entry = tk.Entry(root, textvariable=folder_name_var)

create_folder_button = tk.Button(root, text="Create Folder", command=create_folder)
refresh_button = tk.Button(root, text="Refresh", command=refresh)
start_move_button = tk.Button(root, text="Start Move", command=start_move)
close_button = tk.Button(root, text="Close", command=close_app)

status_label = tk.Label(root, text="Status:")
status_var = tk.StringVar()
status_box = tk.Entry(root, textvariable=status_var, state="readonly")

user_label.grid(row=0, column=0, padx=5, pady=5)
users_combobox.grid(row=0, column=1, padx=5, pady=5)

folder_label.grid(row=1, column=0, padx=5, pady=5)
folders_combobox.grid(row=1, column=1, padx=5, pady=5)

folder_name_label.grid(row=2, column=0, padx=5, pady=5)
folder_name_entry.grid(row=2, column=1, padx=5, pady=5)

create_folder_button.grid(row=3, column=0, padx=5, pady=5)
refresh_button.grid(row=3, column=1, padx=5, pady=5)

start_move_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
close_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

status_label.grid(row=6, column=0, padx=5, pady=5)
status_box.grid(row=6, column=1, padx=5, pady=5)

root.mainloop()

