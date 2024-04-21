# Настройка

Скопируйте файл `.env.dist` в `.env` и задайте значения переменных

# Запуск

Сначала необходимо сбилдить проект

    docker-compose build

Запустить проект

    docker-compose up

Запустить в режиме разработки

    docker-compose -f docker-compose-dev.yml up

Затем просмотреть конечные точки можно по адресу

    http://localhost:8000/docs
