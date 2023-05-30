FROM postgres

# Копируем скрипт внутрь контейнера
COPY ./sql/init.sql /docker-entrypoint-initdb.d/

# Запустить скрипт при старте контейнера
CMD ["postgres"]