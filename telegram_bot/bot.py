import classes
import config
import openai_client.openai_client as openai_client
import database_client.database_client as database_client
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


OPERATING_MODE = classes.OperatingMode(1)

# Check database
if not database_client.check_database():
    exit()


def start(update, context):
    global is_user_exists
    this_user = classes.EffectiveUser(update.effective_user)
    if not this_user.is_bot:
        is_user_exists = database_client.is_user_exists(this_user.id)
        if is_user_exists:
            database_client.delete_user(this_user.id)
        database_client.insert_user(this_user)
    welcome_message = "С возращением" if is_user_exists else "Здравствуйте"
    message = f"{welcome_message} {this_user.full_name}!, я NST2023 bot версии {config.app_version}!"
    context.bot.send_message(chat_id=update.message.chat_id, text=message)


def which_mode(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text=f'Your operating mode is {OPERATING_MODE.name}')


def operate(update, context):
    if OPERATING_MODE == classes.OperatingMode.QUESTION_DA_VINCI:
        get_answer(update.message.text, update, context)


def get_answer(question: str, update, context):
    print('started to processing' + question)
    response = openai_client.turbo(question)
    context.bot.send_message(chat_id=update.message.chat_id, text=response['choices'][0]['message']['content'])
    database_client.insert_log(update.effective_user.id, question, response)


def main():
    updater = Updater(token=config.BOT_TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("mode", which_mode))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, operate))


    updater.start_polling()
    print('Bot started')
    updater.idle()


if __name__ == '__main__':
    main()
