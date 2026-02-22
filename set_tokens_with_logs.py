import os
import requests
import base64
import json
import logging
from urllib3 import disable_warnings

logging.basicConfig(
    filename='league_token_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)

disable_warnings()

LEAGUE_PATH = r"C:\Riot Games\League of Legends\lockfile"

def get_session():
    if not os.path.exists(LEAGUE_PATH):
        logging.error("Lockfile not found. League client appears to be closed.")
        exit("[-] Lockfile not found. Is League even open? (Check league_token_debug.log for details)")

    try:
        with open(LEAGUE_PATH, 'r') as f:
            lockfile_content = f.read()
            _, _, port, password, protocol = lockfile_content.split(':')
            logging.debug(f"Lockfile read successfully. Port: {port}, Protocol: {protocol}")
            
        auth_token = base64.b64encode(f"riot:{password}".encode()).decode()
        
        return {
            'base_url': f"{protocol}://127.0.0.1:{port}",
            'headers': {
                'Authorization': f'Basic {auth_token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        }
    except Exception as e:
        logging.critical(f"Failed to parse lockfile: {e}")
        exit("[-] Critical error reading lockfile.")

def update_identity(token_id):
    session = get_session()
    url = f"{session['base_url']}/lol-challenges/v1/update-player-preferences"
    
    payload = {"challengeIds": [int(token_id)] * 3}

    logging.info(f"Attempting to push Token ID: {token_id}")

    methods = ['PATCH', 'POST', 'PUT']
    
    for m in methods:
        try:
            logging.debug(f"Trying method: {m} on {url}")
            resp = requests.request(
                method=m,
                url=url,
                headers=session['headers'],
                json=payload,
                verify=False,
                timeout=5
            )
            
            if resp.status_code in [200, 204]:
                logging.info(f"Successfully applied via {m}! Status: {resp.status_code}")
                return True
            else:
                logging.warning(f"{m} failed with status {resp.status_code} - Body: {resp.text}")
                
        except Exception as e:
            logging.error(f"Network error on {m}: {e}")

    return False

if __name__ == "__main__":
    print("3x Profile Tokens")
    print("-----------------")
    print("Check 'league_token_debug.log' for detailed logs.")
    
    target_id = input(">> Enter Token ID: ").strip()
    
    if target_id.isdigit():
        logging.info(f"User input received: {target_id}")
        if update_identity(target_id):
            print("\n[+] Done. Switch your Summoner Icon in-game to see the refresh.")
        else:
            print("\n[!] Total failure. Check the log file for the specific error codes.")
    else:
        logging.error(f"Invalid user input: {target_id}")
        print("[-] Please enter a valid number!")
