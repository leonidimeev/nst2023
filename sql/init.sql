-- Создание таблицы logs
CREATE TABLE IF NOT EXISTS logs (
    telegram_id   integer not null,
    request       varchar,
    response      json,
    id            serial constraint logs_pk primary key,
    response_text varchar
);

-- Установка владельца таблицы logs
ALTER TABLE logs OWNER TO postgres;

-- Создание уникального индекса на поле id
CREATE UNIQUE INDEX IF NOT EXISTS logs_id_uindex ON logs (id);

-- Создание таблицы users
CREATE TABLE IF NOT EXISTS users (
    id                          integer not null constraint users_pk primary key,
    added_to_attachment_menu    boolean,
    can_join_groups             boolean,
    can_read_all_group_messages boolean,
    first_name                  varchar(255),
    full_name                   varchar(255),
    is_bot                      boolean,
    is_premium                  boolean,
    last_name                   varchar(255),
    link                        varchar(255),
    name                        varchar(255),
    supports_inline_queries     boolean,
    username                    varchar(255),
    language_code               varchar
);

-- Установка владельца таблицы users
ALTER TABLE users OWNER TO postgres;

-- Создание таблицы chats
CREATE TABLE IF NOT EXISTS chats (
    id      serial,
    log_ids integer[],
    user_id integer,
    name    varchar
);

-- Установка владельца таблицы chats
ALTER TABLE chats OWNER TO postgres;

-- Создание уникального индекса на поле id
CREATE UNIQUE INDEX IF NOT EXISTS chats_id_uindex ON chats (id);

-- Создание таблицы chat_pointer
CREATE TABLE IF NOT EXISTS chat_pointer (
    user_id integer,
    chat_id integer
);

-- Установка владельца таблицы chat_pointer
ALTER TABLE chat_pointer OWNER TO postgres;

-- Создание таблицы user_groups
CREATE TABLE IF NOT EXISTS user_groups (
    user_id    integer,
    group_name varchar
);

-- Установка владельца таблицы user_groups
ALTER TABLE user_groups OWNER TO postgres;
