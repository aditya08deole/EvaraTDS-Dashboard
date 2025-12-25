from dotenv import load_dotenv
import os, requests

# Load environment from backend/.env
load_dotenv('.env')

token = os.getenv('TELEGRAM_BOT_TOKEN')
if not token:
    print('NO_TOKEN')
else:
    try:
        r = requests.get(f'https://api.telegram.org/bot{token}/getMe', timeout=10)
        j = r.json()
        if j.get('ok'):
            # Print only non-sensitive info
            print('BOT_OK', j['result'].get('username'), j['result'].get('first_name'))
        else:
            print('BOT_ERR', j)
    except Exception as e:
        print('ERR', str(e))
