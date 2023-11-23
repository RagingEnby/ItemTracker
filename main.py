import requests
import json
import time
import os

FIRST_EVER_RUN = False

API_URL = "https://api.hypixel.net/resources/skyblock/items"
STORAGE_PATH = "item_data"
if not os.path.exists(STORAGE_PATH):
  FIRST_EVER_RUN = True
  os.makedirs(STORAGE_PATH)
  
JSON_FILE = f"{STORAGE_PATH}/item_data.json"

HISTORY_FILE = f"{STORAGE_PATH}/history"
if not os.path.exists(HISTORY_FILE): os.makedirs(HISTORY_FILE)
  
#CREDIT_FOOTER = requests.get('https://raw.githubusercontent.com/RagingEnby/SkypixelRepo/main/credit_footer.txt').text
CREDIT_FOOTER = 'Made by @ragingenby'
CREDIT_IMAGE = 'https://github.com/RagingEnby/SkypixelRepo/blob/main/pfp.png?raw=true'

BOT_NAME = 'Skypixel'
BOT_AVATAR = 'https://github.com/RagingEnby/SkypixelRepo/blob/main/skypixel.png?raw=true'
# backend url: WEBHOOK_URL = "https://discord.com/api/webhooks/1162537511990612088/z0yLtToP_3T32N8VI1vIUyOG1kvB-k1AuWGhkMt3lrc7De90raGt4yon9mK5u8OXPiwR"
WEBHOOK_URL = "https://discord.com/api/webhooks/1130053094105952276/1M-2qN-zJarywvO_Ck8qnpUtLL9akfjX2IDZRu0RlZ7ONmsqHIJB7UhyN1fy-HBJ7x7o"
dev_mode = False

ITEM_PING = "<@&1130077795234619392>"

def make_json_pretty(json_data):
  print('json_data: ' + str(json_data))
  if "{" in str(json_data):
    formatted_pairs = [f"{key}: {value}" for key, value in json_data.items()]
    print(formatted_pairs)
    return "\n".join(formatted_pairs)
  else:
    return json_data

def SEND_WEBHOOK(CHANGED_CATEGORY, ITEM_ID, CHANGE_TYPE, ITEM_NAME, INFO_ONE, INFO_TWO, CHANGED_FIELD):
  field_one_name = ""
  field_one_value = ""
  field_two_name = ""
  field_two_value = ""
  webhook_content = ""
  webhook_description = ""
  embed_color = 0
  if CHANGED_CATEGORY == "item":
    webhook_content = ITEM_PING
    if CHANGE_TYPE == "added":
      embed_color = 0x55FF55
      webhook_title = f"Item \"{ITEM_NAME}\" ({ITEM_ID}) Added!"
      field_one_name = "Item Info:"
      field_one_value = f"```json\n{make_json_pretty(INFO_ONE)}```"
      
    elif CHANGE_TYPE == "changed":
      embed_color = 0xFFAA00
      webhook_title = f"Item \"{ITEM_NAME}\" ({ITEM_ID}) Modified!"
      field_one_name = "Before:"
      field_one_value = f"```json\n{make_json_pretty(INFO_ONE)}```"
        
      field_two_name = "After:"
      field_two_value = f"```json\n{make_json_pretty(INFO_TWO)}```"
      webhook_description = f"**Changed Field:** \"`{CHANGED_FIELD}`\""
      
    elif CHANGE_TYPE == "removed":
      embed_color = 0xFF5555
      webhook_title = f"Item \"{ITEM_NAME}\" ({ITEM_ID}) Removed!"
      field_one_name = "Item Info:"
      field_one_value = f"```json\n{make_json_pretty(INFO_ONE)}```"
    
    embed = {
      "content": webhook_content,
      "embeds": [
        {
          "url": f"https://wiki.hypixel.net/{ITEM_ID}",
          "description": webhook_description,
          "color": embed_color,
          "fields": [
            {
              "name": field_one_name,
              "value": field_one_value
            },
            {
              "name": field_two_name,
              "value": field_two_value
            }
          ],
          "author": {
            "name": webhook_title,
            "url": f"https://wiki.hypixel.net/{ITEM_ID}",
            "icon_url": f"https://sky.shiiyu.moe/item/{ITEM_ID}"
          },
          "footer": {
            "text": CREDIT_FOOTER,
            "icon_url": CREDIT_IMAGE
          },
          "thumbnail": {
            "url": f"https://sky.shiiyu.moe/item/{ITEM_ID}"
          }
        }
      ],
      "username": BOT_NAME,
      "avatar_url": BOT_AVATAR
    }
    successful_post = False
    while successful_post == False:
        try:
            response = requests.post(WEBHOOK_URL, data=json.dumps(embed), headers={"Content-Type": "application/json"})
            print(response)
            if response.status_code in [200, 204]: successful_post = True
        except Exception as e:
            successful_post = False
            print(e)
            time.sleep(240)
            
            
            
            
    
    

def send_request():
  response = requests.get(API_URL)
  if response.status_code == 200:
    return response.json()
  else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
    return None

def save_data(current_data, previous_data=None):
  if previous_data is not None:
    with open(f'{HISTORY_FILE}/{previous_data["lastUpdated"]}.json', 'w') as file:
      json.dump(previous_data, file)
      file.close()
  with open(f"{HISTORY_FILE}/{current_data['lastUpdated']}.json", "w") as file:
    json.dump(current_data, file)
    file.close()
  with open(JSON_FILE, 'w') as file:
    json.dump(current_data, file)
    file.close()

def load_data():
  try:
    with open(JSON_FILE, "r") as file:
      file_data = json.load(file)
      file.close()
      return file_data
  except FileNotFoundError:
    return None

def compare_data(previous_data, current_data):
  if previous_data is None:
    return

  previous_items = {item["id"]: item for item in previous_data["items"]}
  current_items = {item["id"]: item for item in current_data["items"]}

  for item_id, previous_item in previous_items.items():
    if item_id not in current_items:
      print(f"Item {item_id} has been removed.")
      SEND_WEBHOOK("item", item_id, "removed", previous_item['name'], previous_item, "", "")
    else:
      current_item = current_items[item_id]
      for field, value in previous_item.items():
        if field == "id":
          continue
        if value != current_item.get(field):
          print(f"Item {item_id}: {field} has changed. Previous: {value}, Current: {current_item.get(field)}")
          SEND_WEBHOOK("item", item_id, "changed", current_item['name'], value, current_item.get(field), field)

  for item_id, current_item in current_items.items():
    if item_id not in previous_items:
      print(f"New item detected: {current_item['name']} (ID: {item_id})")
      SEND_WEBHOOK("item", item_id, "added", current_item['name'], current_item, "", "")

while True:
  print("Starting scan...")
  current_data = send_request()
  previous_data = load_data()
  if previous_data['lastUpdated'] != current_data['lastUpdated']:
    save_data(current_data, previous_data)
    compare_data(previous_data, current_data)
  
  print("Finished scan!\n")
  time.sleep(120)
