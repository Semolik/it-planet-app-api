# Запуск

Сначала необходимо сбилдить проект

    docker-compose build

Запустить проект

        docker-compose up

Запустить в режиме разработки

    docker-compose -f docker-compose-dev.yml up

Затем просмотреть конечные точки можно по адресу

    http://localhost:8000/docs

# Миграции

создать миграцию

    docker-compose run api alembic revision --autogenerate -m "migration name"
