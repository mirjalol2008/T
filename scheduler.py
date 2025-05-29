import time
from datetime import datetime, timedelta
from database import get_all_subscriptions, remove_subscription
from telebot import TeleBot

TOKEN = "YOUR_BOT_TOKEN"
VIP_CHANNEL_ID = -1001234567890
bot = TeleBot(TOKEN)

def check_subscriptions():
    subs = get_all_subscriptions()
    now = datetime.now()
    for user_id, expire_date in subs:
        days_left = (expire_date - now).days
        if days_left == 1:
            try:
                bot.send_message(user_id, "📅 Obunangiz tugashiga 1 kun qoldi. Iltimos, uzaytiring.")
            except Exception as e:
                print(f"Ogohlantirish jo'natishda xatolik: {e}")
        elif days_left < 0:
            # Obuna muddati tugagan, kanalidan chiqarish
            try:
                bot.kick_chat_member(VIP_CHANNEL_ID, user_id)
                remove_subscription(user_id)
                print(f"Foydalanuvchi {user_id} kanaldan chiqarildi.")
            except Exception as e:
                print(f"Foydalanuvchini chiqarishda xatolik: {e}")

if __name__ == "__main__":
    while True:
        check_subscriptions()
        time.sleep(3600*24)  # Har 24 soatda tekshirish