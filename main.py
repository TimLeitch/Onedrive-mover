
import requests
from dotenv import dotenv_values

config = dotenv_values('.env')

def get_token(): #gets access token
    
    uri = (f"https://login.microsoftonline.com/{config['TENANT_ID']}/oauth2/v2.0/token")
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
def get_users():#probally not needed
    headers = {"Authorization": f"Bearer {get_token()}"}
    url = config['BASE_URI']+ "/users?$top-999$orderby=displayName"
    response = requests.get(url, headers=headers)
    print(response.json())  
def get_user_drive(upn): #returns users drive
    headers = {"Authorization": f"Bearer {get_token()}"}
    url = f'https://graph.microsoft.com/v1.0/users/{upn}/drive'
    response = requests.get(url, headers=headers)
    # print(response.json()) 
    return response.json() 
def get_items_in_drive(upn):#returns all items in users drive
    headers = {"Authorization": f"Bearer {get_token()}"}
    url = f'https://graph.microsoft.com/v1.0/users/{upn}/drive/root/children'
    res = requests.get(url, headers=headers)
    #handle pagination             
    while '@odata.nextLink' in res.json():
        #append rest of data to response
        response = requests.get(res.json()['@odata.nextLink'], headers=headers)
        res.json()['value'].extend(response.json()['value'])
        res.json()['@odata.nextLink'] = response.json()['@odata.nextLink']
    # print(res.json())
    return res.json()
def get_ee_folder_ids():#returns all folders in EE drive
    headers = {"Authorization": f"Bearer {get_token()}"}
    url = f'https://graph.microsoft.com/v1.0/users/ced1d981-4c26-42d8-af9b-475165161e93/drive/root/children'
    res = requests.get(url, headers=headers)
    #handle pagination             
    while '@odata.nextLink' in res.json():
        #append rest of data to response
        response = requests.get(res.json()['@odata.nextLink'], headers=headers)
        res.json()['value'].extend(response.json()['value'])
        res.json()['@odata.nextLink'] = response.json()['@odata.nextLink']
    # print(res.json())
    return res.json()
def check_if_folder_exists(folder_name):#returns folder id if it exists
    folders = get_ee_folder_ids()
    for folder in folders['value']:
        if folder['name'] == folder_name:
            return folder['id']
    #TODO: create folder if it doesnt exist
    return None

def move_item_to_drive(upn, item_id, folder_name): #moves item to ee drive
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
    
def main():
    # get all items in users drive
    user_to_move = input("Enter user to move: (UPN/MAIL)")
    folder_name = input("Enter folder name to move to: ")
    items = get_items_in_drive(user_to_move)
    
    for item in items['value']:
        print(item['name'])
        move_item_to_drive(user_to_move, item['id'], folder_name)
    
if __name__ == "__main__":
    main()
    
    
#TODO: get status of moves 
#TODO: create folder if it doesnt exist
#TODO: delete original item after move is complete
#TODO: create a log of all moves
#TODO: create a GUI
