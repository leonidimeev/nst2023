from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
import configparser
import classes
import openai_client.client as openai_client


BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Create a ConfigParser object and read the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# Get the value of a configuration setting
app_name = config.get('app', 'name')
app_version = config.getfloat('app', 'version')
app_debug = config.getboolean('app', 'debug')

OPERATING_MODE = classes.OperatingMode(1)


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Hello, I'm a NST2023 bot! Available commands: /mode")


def which_mode(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text=f'Your operating mode is {OPERATING_MODE.name}')


def operate(update, context):
    if OPERATING_MODE == classes.OperatingMode.QUESTION_DA_VINCI:
        get_answer(update.message.text, update, context)


def get_answer(question: str, update, context):
    print('started to precessing' + question)
    # response = openai_client.test(question)
    # context.bot.send_message(chat_id=update.message.chat_id, text=response['choices'][0]['message'])

    response = openai_client.turbo(question)
    context.bot.send_message(chat_id=update.message.chat_id, text=response['choices'][0]['message']['content'])


def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("mode", which_mode))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, operate))


    updater.start_polling()
    print('Bot started')
    updater.idle()


if __name__ == '__main__':
    main()
