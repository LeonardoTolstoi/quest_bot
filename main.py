import logging, json
from sys import prefix

from telegram import Update, ForceReply, message, update
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
users = json.loads(open("users.json").read())
priv_keys = list(map(int, open("priv_keys.txt").read().split()))

def start(update: Update, context: CallbackContext) -> None:
    context.user_data['waiting_for_key'] = True
    update.message.reply_text("Введите ваш приватный ключ: ")

def insert_user(context: CallbackContext) -> None:
    input_key = context.job.context['input_key']
    chat_id = int(context.job.context['chat_id'])
    username = context.job.context['username']
    if username in users:
        if users[username] == input_key:
            context.bot.send_message(text="Вы уже авторизированы", chat_id = chat_id)
        else:
            context.bot.send_message(text="Вы уже авторизированы под другим ключом", chat_id = chat_id)
    else:
        if input_key in users.keys():
            context.bot.send_message(text="Ключ уже занят", chat_id = chat_id)
        else:
            users[username] = input_key
            context.bot.send_message(text="Вы авторизированы", chat_id = chat_id)
            open("users.json", "w").write(json.dumps(users))

def message_handler(update: Update, context: CallbackContext) -> None:
    if 'waiting_for_key' in context.user_data:
        if context.user_data['waiting_for_key']:
            if update.message.text.isnumeric():
                context.job_queue.run_once(
                    insert_user, 0, context={
                        "chat_id" : update.message.chat_id,
                        "username" : update.message.from_user.username,
                        "input_key" : int(update.message.text),
                    }
                )
            else:
                update.message.reply_text("Ключ является числом")
    else:
        update.message.reply_text("Чтобы начать работу введите /start")

def hint(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.username in users:
        hints = open("hints.txt", "r", encoding='utf-8')
        update.message.reply_text(hints.read())
    else:
        update.message.reply_text("Вы не авторизованы")

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("1123025521:AAGYCUf_-FzXQ1MhtDFTHl74R2yhEZOzoBw")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("hint", hint))
    

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))    

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()