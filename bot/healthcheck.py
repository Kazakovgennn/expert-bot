import requests
from core.config import settings

def check_bot():
    try:
        response = requests.get(f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getMe", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    if check_bot():
        print("✅ Бот работает")
    else:
        print("❌ Бот не отвечает")
