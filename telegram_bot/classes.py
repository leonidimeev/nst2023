import json

import telegram
from enum import Enum


# Operating mode
class OperatingMode(Enum):
    QUESTION_DA_VINCI = 1


# Telegram user
class EffectiveUser:
    def __init__(self, id=None, added_to_attachment_menu=None, can_join_groups=None, can_read_all_group_messages=None,
                 first_name=None, full_name=None, is_bot=None, is_premium=None, language_code=None, last_name=None,
                 link=None, name=None, supports_inline_queries=None, username=None):
        # Перегрузка для создания из объекта telegram.user.User
        if isinstance(id, telegram.user.User):
            self.from_telegram_user(id)
        else:
            self.id = id
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
    def to_dict(self):
        return {
            'id': self.id,
            'added_to_attachment_menu': self.added_to_attachment_menu,
            'can_join_groups': self.can_join_groups,
            'can_read_all_group_messages': self.can_read_all_group_messages,
            'first_name': self.first_name,
            'full_name': self.full_name,
            'is_bot': self.is_bot,
            'is_premium': self.is_premium,
            'last_name': self.last_name,
            'link': self.link,
            'name': self.name,
            'supports_inline_queries': self.supports_inline_queries,
            'username': self.username
        }

    @classmethod
    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_obj):
        obj_dict = json.loads(json_obj)
        return cls(**obj_dict)

    @classmethod
    def from_telegram_user(self, user):
            self.id = user.id
            self.added_to_attachment_menu = user.added_to_attachment_menu
            self.can_join_groups = user.can_join_groups
            self.can_read_all_group_messages = user.can_read_all_group_messages
            self.first_name = user.first_name
            self.full_name = user.full_name
            self.is_bot = user.is_bot
            self.is_premium = user.is_premium
            self.language_code = user.language_code
            self.last_name = user.last_name
            self.link = user.link
            self.name = user.name
            self.supports_inline_queries = user.supports_inline_queries
            self.username = user.username