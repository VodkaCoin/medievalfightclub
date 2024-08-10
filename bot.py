from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, CallbackContext
from pymongo import MongoClient
import logging

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Подключение к MongoDB
client = MongoClient("mongodb+srv://cryptonewsorg:fSOeFabxwXzVZCEE@cluster0.ynwya.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["medieval_fight_club"]
users = db["users"]

# Ваш Telegram Bot API Token
API_TOKEN = '7027516384:AAFWLmj7xX69TKWJs2CW-paGjUS0gAiRXqU'

# Словари с текстами на разных языках
texts = {
    'en': {
        'welcome': "Welcome to Medieval Fight Club! An exciting multiplayer role-playing online game is coming soon!",
        'subscribe_channel': "Subscribe to the channel",
        'subscribe_twitter': "Follow on Twitter",
        'invite_friends': "Invite friends",
        'learn_more': "Learn more",
        'invite_text': "Invite friends using this link and earn 10 MFC coins for each invited friend:\n",
        'select_language': "Please select your language:",
        'language_selected': "You have selected English."
    },
    'ru': {
        'welcome': "Добро пожаловать в Medieval Fight Club! Захватывающая многопользовательская ролевая онлайн-игра скоро выйдет!",
        'subscribe_channel': "Подписаться на канал",
        'subscribe_twitter': "Подписаться на Twitter",
        'invite_friends': "Пригласить друзей",
        'learn_more': "Узнать больше",
        'invite_text': "Пригласите друзей по этой ссылке и получите 10 монет MFC за каждого приглашенного:\n",
        'select_language': "Пожалуйста, выберите язык:",
        'language_selected': "Вы выбрали русский язык."
    }
}

async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("English", callback_data='lang_en')],
        [InlineKeyboardButton("Русский", callback_data='lang_ru')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(texts['en']['select_language'], reply_markup=reply_markup)

async def set_language(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    lang = query.data.split('_')[1]  # 'en' или 'ru'

    # Обновление данных пользователя с указанием выбранного языка
    users.update_one({"user_id": user_id}, {"$set": {"language": lang}}, upsert=True)
    await query.message.reply_text(texts[lang]['language_selected'])
    await show_main_menu(update, context, lang)

async def show_main_menu(update: Update, context: CallbackContext, lang: str):
    keyboard = [
        [InlineKeyboardButton(texts[lang]['subscribe_channel'], url="https://t.me/YOUR_CHANNEL")],
        [InlineKeyboardButton(texts[lang]['subscribe_twitter'], url="https://twitter.com/YOUR_TWITTER")],
        [InlineKeyboardButton(texts[lang]['invite_friends'], callback_data='invite_friends')],
        [InlineKeyboardButton(texts[lang]['learn_more'], url="https://YOUR_WEBSITE.com")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = texts[lang]['welcome']
    await update.message.reply_text(message, reply_markup=reply_markup)

async def invite_friends(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    user = users.find_one({"user_id": user_id})
    lang = user.get('language', 'en')  # Если языка нет, используем английский
    referral_link = f"https://t.me/MedievalFightClubBeta_bot?start={user_id}"
    message = texts[lang]['invite_text'] + referral_link
    await context.bot.send_message(chat_id=user_id, text=message)

async def handle_referral(update: Update, context: CallbackContext):
    args = context.args
    user_id = update.message.from_user.id
    if len(args) > 0:
        referrer_id = int(args[0])
        if users.find_one({"user_id": referrer_id}):
            users.update_one({"user_id": referrer_id}, {"$inc": {"mfc_coins": 10, "referrals": 1}})
    await start(update, context)

def main():
    application = ApplicationBuilder().token(API_TOKEN).build()
    application.add_handler(CommandHandler("start", handle_referral))
    application.add_handler(CallbackQueryHandler(set_language, pattern='lang_'))
    application.add_handler(CallbackQueryHandler(invite_friends, pattern='invite_friends'))
    application.run_polling()

if __name__ == '__main__':
    main()
