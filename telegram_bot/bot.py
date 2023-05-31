from telegram import ReplyKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters

import classes
import config
import database_client.database_client as database_client
import openai_client.openai_client as openai_client
import timetable_module.timetable_module as timetable_module

OPERATING_MODE = classes.OperatingMode(1)

# Определение стадий (шагов) диалога add_group
ADD_GROUP_STEP_1 = 1

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
            created_chat = database_client.create_chat(None, this_user.id, None)
            # Создание нового указателя пользователя
            database_client.create_chat_pointer(this_user.id, created_chat[0])
    else:
        this_user = classes.EffectiveUser(update.effective_user)
    return this_user


def generate_main_keyboard():
    # Create a list of available functions
    buttons = [
        "Мои чаты", "Новый чат", "Мой профиль", "Мое расписание"
    ]
    return ReplyKeyboardMarkup([buttons], resize_keyboard=True)


def handle_function_command(update, context):
    text = update.effective_message.text
    this_user = detect_user(update, initial=False)

    if text == "Мои чаты":
        my_chats(update, context, this_user)
    elif text == "Новый чат":
        new_chat(update, context, this_user)
    elif text == "Мой профиль":
        my_profile(update, context, this_user)
    elif text == "Мое расписание":
        my_timetable(update, context, this_user)
    else:
        operate(update, context, this_user)


def start(update, context):
    this_user = detect_user(update, initial=True)
    welcome_message = "С возращением" if is_user_exists else "Здравствуйте"
    message = f"{welcome_message} {this_user.full_name}!, я NST2023 bot версии {config.app_version}!\n"
    # Send the message with the functions and buttons
    function_message = "Функции:\n=====================\n"
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=message + function_message,
        reply_markup=generate_main_keyboard())


def my_chats(update, context, this_user):
    chats = []
    for chats_raw in database_client.get_chats(user_id=this_user.id):
        chats.append(classes.Chats.from_tuple(chats_raw))
    if len(chats) == 0:
        context.bot.send_message(chat_id=update.message.chat_id, text="У вас нет ни одного созданного чата!",
                                 reply_markup=generate_main_keyboard())
    else:
        chat_pointer_raw = database_client.get_chat_pointer(this_user.id)
        if chat_pointer_raw is None:
            database_client.create_chat_pointer(this_user.id, chats[0].id)
            chat_pointer_raw = database_client.get_chat_pointer(this_user.id)
        this_user_chat_pointer = classes.ChatPointer.from_tuple(chat_pointer_raw)
        response_message = f"Ваши чаты, чтобы переключится, нажмите на айди:\n"
        chat_list_pointer = 1
        for user_chat in chats:
            if this_user_chat_pointer.chat_id == user_chat.id:
                response_message += f"/chat_{chat_list_pointer}:chat{user_chat.id} ({user_chat.name})   (актуальный чат)  удалить? -> /delete_chat_{chat_list_pointer}\n"
            else:
                response_message += f"/chat_{chat_list_pointer}:chat{user_chat.id} ({user_chat.name})  удалить? -> /delete_chat_{chat_list_pointer}\n "
            chat_list_pointer += 1
        # Send the message with the functions and buttons
        context.bot.send_message(chat_id=update.message.chat_id, text=response_message,
                                 reply_markup=generate_main_keyboard())


def my_profile(update, context, this_user):
    response_message = ""
    response_message += f"fullname: {this_user.full_name}\n"
    response_message += f"username: {this_user.username}\n"
    response_message += f"id: {this_user.id}\n"
    response_message += f"is_bot: {this_user.is_bot}\n"
    response_message += f"added_to_attachment_menu: {this_user.added_to_attachment_menu}\n"
    response_message += f"can_join_groups: {this_user.can_join_groups}\n"
    response_message += f"can_read_all_group_messages: {this_user.can_read_all_group_messages}\n"

    number_of_chats = len(database_client.get_chats(this_user.id))
    response_message += f"number_of_chats: {number_of_chats}\n"

    user_groups = []
    user_groups_raw = database_client.get_user_groups(this_user.id)
    for group in user_groups_raw:
        user_groups.append(classes.UserGroups.from_tuple(group))
    response_message += f"user_groups:\n"
    for user_group in user_groups:
        response_message += f"- {user_group.group_name}\n"
    response_message += f"/add_group  <- добавить группу\n"
    response_message += f"/delete_groups  <- удалить все группы\n"

    # Send the message with the functions and buttons
    context.bot.send_message(chat_id=update.message.chat_id, text=response_message, reply_markup=generate_main_keyboard())


def my_timetable(update, context, this_user):
    response_message = ""
    user_groups_raw = database_client.get_user_groups(this_user.id)
    if len(user_groups_raw) == 0:
        response_message += f"Не найдены группы!\n"
    else:
        user_groups = []
        for group_raw in user_groups_raw:
            user_groups.append(classes.UserGroups.from_tuple(group_raw))
        timetables = {}
        for user_group in user_groups:
            timetables[user_group.group_name] = timetable_module.get_timetable(user_group.group_name)
        for group_name, timetable in timetables.items():
            response_message += f"Для группы <b>{group_name}</b>:\n"
            if len(timetable) == 0:
                response_message += f"Не найдено расписание!\n"
            else:
                for week_day, day_lessons_raw in timetable.items():
                    response_message += f"========================\n"
                    response_message += f"<b>{week_day}</b>\n"
                    for index, lessons_raw in enumerate(day_lessons_raw):
                        lesson = classes.Lesson.from_tuple(lessons_raw)
                        response_message += f"<b>{index + 1} {lesson.time}: {lesson.subject}</b>\n" \
                                            f"{lesson.classroom} {lesson.teacher}\n" \
                                            f"{lesson.additional_info}\n"

    # Send the message with the functions and buttons
    context.bot.send_message(chat_id=update.message.chat_id, text=response_message, reply_markup=generate_main_keyboard(), parse_mode=ParseMode.HTML)


def new_chat(update, context, this_user):
    this_user_chats = database_client.get_chats(this_user.id)
    if len(this_user_chats) >= config.app_user_max_chats:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=f"Максимальное количество чатов для польователя: 5! Пользователь: {this_user.username} id: {this_user.id}")
    else:
        created_chat = classes.Chats.from_tuple(database_client.create_chat(None, this_user.id, []))
        this_user_chat_pointer_raw = database_client.get_chat_pointer(this_user.id)
        # Когда у пользователя нет chat_pointer
        if this_user_chat_pointer_raw is None:
            database_client.create_chat_pointer(this_user.id, created_chat.id)
        else:
            database_client.update_chat_pointer(this_user.id, created_chat.id)
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Создан новый чат: {created_chat.id}\n",
                                 reply_markup=generate_main_keyboard())


def operate(update, context, this_user):
    question = update.message.text
    print('started to processing' + question)
    # Указатель чата пользователя
    chat_pointer_raw = database_client.get_chat_pointer(this_user.id)
    if chat_pointer_raw is None:
        new_chat(update, context, this_user)
        chat_pointer_raw = database_client.get_chat_pointer(this_user.id)
    chat_pointer = classes.ChatPointer.from_tuple(chat_pointer_raw)
    user_chat = classes.Chats.from_tuple(database_client.get_chat(chat_pointer.chat_id))
    chat_logs = []
    if user_chat.log_ids is None:
        user_chat.log_ids = []
    for log_id in user_chat.log_ids:
        chat_logs.append(classes.Logs.from_tuple(database_client.get_log(log_id)))
    # Генерация промта с историей
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    sorted_chat_logs = sorted(chat_logs, key=lambda chat_log: chat_log.id)
    for log in sorted_chat_logs:
        messages.append({"role": "user", "content": f"{log.request}"})
        messages.append({"role": "assistant", "content": f"{log.response_text}"})
    # Добавление вопроса
    messages.append({"role": "assistant", "content": f"{question}"})
    response = openai_client.turbo(messages)
    response_text = response['choices'][0]['message']['content']
    context.bot.send_message(chat_id=update.message.chat_id, text=response_text)

    log = classes.Logs.from_tuple(database_client.insert_log(update.effective_user.id, question, response, response_text))
    if user_chat.name is None:
        splitted_question_text = log.response_text.split()
        user_chat.name = ' '.join(splitted_question_text[:5])
    user_chat.log_ids.append(log.id)
    database_client.update_chat(user_chat.id, user_chat.name, this_user.id, user_chat.log_ids)


def change_chat_pointer(update, context, user, chat_id):
    this_chat = classes.Chats.from_tuple(database_client.get_chat(chat_id))
    if user.id != this_chat.user_id:
        permission_denied_message(update, context, user, f"переключение на чат. chat_id: {this_chat.id}")
    else:
        database_client.update_chat_pointer(user.id, chat_id)
    context.bot.send_message(chat_id=update.message.chat_id, text=f"Переключено на чат:{chat_id}!")


def permission_denied_message(update, context, user, message):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=f"Недостаточно прав для {message}. Пользователь: {user.username} id: {user.id}")


def chat(update, context):
    this_user = classes.EffectiveUser(update.effective_user)
    this_chat = classes.Chats.from_tuple(database_client.get_chat_by_order(this_user.id, 0))
    change_chat_pointer(update, context, this_user, this_chat.id)


def add_group(update, context):
    update.message.reply_text("Введите название группы (пример: ИМИ-М-НОД-21)")
    return ADD_GROUP_STEP_1


def add_group_handle_answer(update, context):
    answer = update.message.text
    this_user = classes.EffectiveUser(update.effective_user)
    database_client.insert_user_group(this_user.id, answer)
    update.message.reply_text(f"Добавлена группа: {answer}")
    my_profile(update, context, this_user)
    return ConversationHandler.END


def delete_groups(update, context):
    this_user = classes.EffectiveUser(update.effective_user)
    database_client.delete_user_groups(this_user.id)
    context.bot.send_message(chat_id=update.message.chat_id, text="Удалены все группы пользователя")
    my_profile(update, context, this_user)


# region chat_selector
def select_chat(update, context, index):
    this_user = classes.EffectiveUser(update.effective_user)
    this_chat = classes.Chats.from_tuple(database_client.get_chat_by_order(this_user.id, index))
    change_chat_pointer(update, context, this_user, this_chat.id)


def chat_1(update, context):
    select_chat(update, context, 1)


def chat_2(update, context):
    select_chat(update, context, 2)


def chat_3(update, context):
    select_chat(update, context, 3)


def chat_4(update, context):
    select_chat(update, context, 4)


def chat_5(update, context):
    select_chat(update, context, 5)
# endregion


# region chat_deleter
def delete_chat(update, context, index):
    this_user = classes.EffectiveUser(update.effective_user)
    this_user_chats = database_client.get_chats(this_user.id)

    if index < len(this_user_chats):
        this_chat = classes.Chats.from_tuple(this_user_chats[index])
        this_user_chat_pointer = classes.ChatPointer.from_tuple(database_client.get_chat_pointer(this_user.id))
        database_client.delete_chat(this_chat.id)
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Удален чат:{this_chat.id}!")

        if this_user_chat_pointer.chat_id == this_chat.id:
            database_client.delete_chat_pointer(this_user.id, this_chat.id)


def delete_chat_1(update, context):
    delete_chat(update, context, 0)


def delete_chat_2(update, context):
    delete_chat(update, context, 1)


def delete_chat_3(update, context):
    delete_chat(update, context, 2)


def delete_chat_4(update, context):
    delete_chat(update, context, 3)


def delete_chat_5(update, context):
    delete_chat(update, context, 4)


# endregion


def main():
    updater = Updater(token=config.BOT_TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("chat", chat))

    # region groups
    # Создание и регистрация ConversationHandler для add_group
    add_group_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add_group', add_group)],
        states={
            ADD_GROUP_STEP_1: [MessageHandler(Filters.text, add_group_handle_answer)],
        },
        fallbacks=[],
    )
    dp.add_handler(add_group_conv_handler)
    dp.add_handler(CommandHandler("delete_groups", delete_groups))
    # endregion

    # region chat_selector_and_deleter
    dp.add_handler(CommandHandler("chat_1", chat_1))
    dp.add_handler(CommandHandler("chat_2", chat_2))
    dp.add_handler(CommandHandler("chat_3", chat_3))
    dp.add_handler(CommandHandler("chat_4", chat_4))
    dp.add_handler(CommandHandler("chat_5", chat_5))
    dp.add_handler(CommandHandler("delete_chat_1", delete_chat_1))
    dp.add_handler(CommandHandler("delete_chat_2", delete_chat_2))
    dp.add_handler(CommandHandler("delete_chat_3", delete_chat_3))
    dp.add_handler(CommandHandler("delete_chat_4", delete_chat_4))
    dp.add_handler(CommandHandler("delete_chat_5", delete_chat_5))
    # endregionn

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_function_command))

    updater.start_polling()
    print('Bot started')
    updater.idle()


if __name__ == '__main__':
    main()
