import classes
import config
import openai_client.openai_client as openai_client
from telegram import KeyboardButton, ReplyKeyboardMarkup
import database_client.database_client as database_client
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


OPERATING_MODE = classes.OperatingMode(1)

# Check database
if not database_client.check_database():
    exit()


def detect_user(update, initial: bool):
    if initial:
        global is_user_exists
        this_user = classes.EffectiveUser(update.effective_user)
        if not this_user.is_bot:
            is_user_exists = database_client.is_user_exists(this_user.id)
            if is_user_exists:
                database_client.delete_user(this_user.id)
            # Создание нового пользователя
            database_client.insert_user(this_user)
            # Создание нового чата
            new_chat = database_client.create_chat(None, this_user.id, None)
            # Создание нового указателя пользователя
            database_client.create_chat_pointer(this_user.id, new_chat[0])
    else:
        this_user = classes.EffectiveUser(update.effective_user)
    return this_user


def generate_main_keyboard():
    # Create a list of available functions
    buttons = [
        "Мои чаты", "Новый чат"
    ]
    return ReplyKeyboardMarkup([buttons], resize_keyboard=True)


def start(update, context):
    this_user = detect_user(update, initial=True)
    welcome_message = "С возращением" if is_user_exists else "Здравствуйте"
    message = f"{welcome_message} {this_user.full_name}!, я NST2023 bot версии {config.app_version}!\n"
    # Send the message with the functions and buttons
    function_message = "Функции:\n=====================\n"
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=message+function_message,
        reply_markup=generate_main_keyboard())


def my_chats(update, context, this_user):
    chats = []
    for chats_raw in database_client.get_chats(user_id=this_user.id):
        chats.append(classes.Chats.from_tuple(chats_raw))
    this_user_chat_pointer = classes.ChatPointer.from_tuple(database_client.get_chat_pointer(this_user.id))
    response_message = f"Ваши чаты, чтобы переключится, нажмите на айди:\n"
    for chat in chats:
        if this_user_chat_pointer.chat_id == chat.id:
            response_message += f"/chat_{chat.id}_{chat.name}   (актуальный чат)   удалить? -> /delete_chat_{chat.id}\n"
        else:
            response_message += f"/chat_{chat.id}_{chat.name}    удалить? -> /delete_chat_{chat.id}\n"
    # Send the message with the functions and buttons
    context.bot.send_message(chat_id=update.message.chat_id, text=response_message, reply_markup=generate_main_keyboard())


def new_chat(update, context, this_user):
    chat = classes.Chats.from_tuple(database_client.create_chat(None, this_user.id, []))
    response_message = f"Создан новый чат: {chat.id}\n"
    database_client.update_chat_pointer(this_user.id, chat.id)
    context.bot.send_message(chat_id=update.message.chat_id, text=response_message, reply_markup=generate_main_keyboard())


def operate(update, context, this_user):
    question = update.message.text
    print('started to processing' + question)
    # Указатель чата пользователя
    chat_pointer = classes.ChatPointer.from_tuple(database_client.get_chat_pointer(this_user.id))
    # Чат пользователя
    chat = database_client.get_chat(chat_pointer.chat_id)
    chat_logs = []
    for log_id in chat.log_ids:
        chat_logs.append(classes.Logs.from_tuple(database_client.get_log(log_id)))
    # Генерация промта с историей
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    sorted_chat_logs = sorted(chat_logs, key=lambda log: log.id)
    for log in sorted_chat_logs:
        messages.append({"role": "user", "content": f"{log.request}"})
        messages.append({"role": "assistant", "content": f"{log.response_text}"})
    # Добавление вопроса
    messages.append({"role": "assistant", "content": f"{question}"})
    response = openai_client.turbo(messages)
    context.bot.send_message(chat_id=update.message.chat_id, text=response['choices'][0]['message']['content'])
    database_client.insert_log(update.effective_user.id, question, response)


def change_chat_pointer(update, context, user, chat_id):
    this_chat = database_client.get_chat(chat_id)
    if user.id != this_chat.user_id:
        permission_denied_message(update, context, user, f"переключение на чат. chat_id: {this_chat.id}")


def permission_denied_message(update, context, user, message):
    context.bot.send_message(chat_id=update.message.chat_id, text=f"Недостаточно прав для {message}. Пользователь: {user.username} id: {user.id}")


def handle_function_command(update, context):
    text = update.effective_message.text
    this_user = detect_user(update, initial=False)

    if text == "Мои чаты":
        my_chats(update, context, this_user)
    elif text == "Новый чат":
        new_chat(update, context, this_user)
    elif text.startswith('/'):
        command = text.split('_')
        # Команда переключения между чатами
        if command[0] == 'chat' and len(command) == 3:
            change_chat_pointer(update, context, this_user, command[1])
        # Команда удаления чата
        elif command[0] == 'delete' and command[1] == 'chat' and len(command) == 3:
            delete_chat(command[2])
    else:
        operate(update, context, this_user)


def main():
    updater = Updater(token=config.BOT_TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_function_command))

    updater.start_polling()
    print('Bot started')
    updater.idle()


if __name__ == '__main__':
    main()
