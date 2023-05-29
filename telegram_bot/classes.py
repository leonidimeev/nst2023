import json

import telegram
from enum import Enum


# Operating mode
class OperatingMode(Enum):
    QUESTION_DA_VINCI = 1


# Telegram user
class EffectiveUser:
    def __init__(self, user_id=None, added_to_attachment_menu=None, can_join_groups=None, can_read_all_group_messages=None,
                 first_name=None, full_name=None, is_bot=None, is_premium=None, language_code=None, last_name=None,
                 link=None, name=None, supports_inline_queries=None, username=None):
        # Перегрузка для создания из объекта telegram.user.User
        if isinstance(user_id, telegram.user.User):
            self.from_telegram_user(user_id)
        else:
            self.id = user_id
            self.added_to_attachment_menu = added_to_attachment_menu
            self.can_join_groups = can_join_groups
            self.can_read_all_group_messages = can_read_all_group_messages
            self.first_name = first_name
            self.full_name = full_name
            self.is_bot = is_bot
            self.is_premium = is_premium
            self.language_code = language_code
            self.last_name = last_name
            self.link = link
            self.name = name
            self.supports_inline_queries = supports_inline_queries
            self.username = username

    @classmethod
    def from_json(cls, json_obj):
        obj_dict = json.loads(json_obj)
        return cls(**obj_dict)

    @classmethod
    def from_telegram_user(cls, user):
        cls.id = user.id
        cls.added_to_attachment_menu = user.added_to_attachment_menu
        cls.can_join_groups = user.can_join_groups
        cls.can_read_all_group_messages = user.can_read_all_group_messages
        cls.first_name = user.first_name
        cls.full_name = user.full_name
        cls.is_bot = user.is_bot
        cls.is_premium = user.is_premium
        cls.language_code = user.language_code
        cls.last_name = user.last_name
        cls.link = user.link
        cls.name = user.name
        cls.supports_inline_queries = user.supports_inline_queries
        cls.username = user.username


# Указатель чата
class ChatPointer:
    def __init__(self, user_id, chat_id):
        self.user_id = user_id
        self.chat_id = chat_id

    @classmethod
    def from_tuple(cls, tuple_data):
        return cls(*tuple_data)


# Чат
class Chats:
    def __init__(self, chat_id, log_ids, user_id, name):
        self.id = chat_id
        self.log_ids = log_ids
        self.user_id = user_id
        self.name = name

    @classmethod
    def from_tuple(cls, tuple_data):
        chat_id, log_ids, user_id, name = tuple_data
        return cls(chat_id, log_ids, user_id, name)


# Логи
class Logs:
    def __init__(self, telegram_id, request, response, log_id, response_text):
        self.telegram_id = telegram_id
        self.request = request
        self.response = response
        self.id = log_id
        self.response_text = response_text

    @classmethod
    def from_tuple(cls, tuple_data):
        telegram_id, request, response, log_id, response_text = tuple_data
        return cls(telegram_id, request, response, log_id, response_text)


# Группы
class UserGroups:
    def __init__(self, user_id, group_name):
        self.user_id = user_id
        self.group_name = group_name

    @classmethod
    def from_tuple(cls, tuple_data):
        user_id, group_name = tuple_data
        return cls(user_id, group_name)


# Занятие
class Lesson:
    def __init__(self, time, subject, teacher, classroom, additional_info):
        self.time = time
        self.subject = subject
        self.teacher = teacher
        self.classroom = classroom
        self.additional_info = additional_info

    @classmethod
    def from_tuple(cls, tuple_data):
        time, subject, teacher, classroom, additional_info = tuple_data
        return cls(time, subject, teacher, classroom, additional_info)
