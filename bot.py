import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import *
from datetime import datetime, timedelta

TOKEN = "YOUR_BOT_TOKEN"
ADMIN_ID = YOUR_ADMIN_TELEGRAM_ID  # int
VIP_CHANNEL_ID = -1001234567890     # yopiq kanal ID sini shu yerga yozing

bot = telebot.TeleBot(TOKEN)

def generate_month_buttons(user_id, extend=False):
    mode = "extend" if extend else "new"
    markup = InlineKeyboardMarkup()
    for m in [1, 3, 6, 12]:
        markup.add(InlineKeyboardButton(f"{m} oy", callback_data=f"confirm_{user_id}_{m}_{mode}"))
    markup.add(InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    text = (
        "👋 Salom! Obunani to‘lash uchun kartamiz:\n\n"
        "💳 8600 1234 5678 9012\n\n"
        "Obuna uchun chekni botga yuboring"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(content_types=['photo'])
def handle_check_photo(message):
    user_id = message.from_user.id

    # Agar foydalanuvchi avvaldan obunani uzaytirishni xohlagan bo'lsa (oddiy qilib, har doim false)
    extend = get_subscription(user_id) is not None

    caption = f"{'♻️' if extend else '🆕'} {user_id} {'obunasini uzaytirmoqchi' if extend else 'yangi obuna uchun'} chek yubordi. Necha oylik berilsin?"
    markup = generate_month_buttons(user_id, extend)

    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def handle_confirm(call):
    _, user_id, months, mode = call.data.split("_")
    user_id = int(user_id)
    months = int(months)

    new_expire = add_subscription(user_id, months)

    bot.send_message(user_id, f"✅ Obunangiz {months} oyga {'uzaytirildi' if mode=='extend' else 'faollashtirildi'}.\n📅 Yangi tugash sanasi: {new_expire.date()}")

    # Foydalanuvchini yopiq kanalga qo'shish
    try:
        bot.unban_chat_member(VIP_CHANNEL_ID, user_id)  # Avval chiqarilgan bo'lsa tiklash uchun
        bot.invite_link_create(VIP_CHANNEL_ID)
        bot.approve_chat_join_request(VIP_CHANNEL_ID, user_id)
    except Exception as e:
        print(f"Kanalga qo'shishda xatolik: {e}")

    bot.answer_callback_query(call.id, "Tasdiqlandi!")

@bot.callback_query_handler(func=lambda call: call.data == "cancel")
def cancel_callback(call):
    bot.answer_callback_query(call.id, "Bekor qilindi")

if __name__ == "__main__":
    bot.infinity_polling()