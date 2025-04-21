# iBook
__Backend__ часть для книжного маркетплейса `ibook`, написаная на современном асинхронном FastAPI, детальнее - используются так же PostgreSQL, RabbitMQ, Celery, Alembic, SQLAlchemy, pytest, gunicorn. Дополнительно проект настроен на использование `Stripe` для оплаты заказов на книги.
## Установка
```bash
git clone https://github.com/involved-entity/ibook
cd ibook
docker-compose up
```
Проект будет запущен в продакшен режиме на `http://localhost/`, документация - `http://localhost/docs`
## Функционал
Пользователи имеют роли `ADMIN`, `SELLER`, `CUSTOMER` и соответствующие ролям права. Реализована логика заказов, отзывов, категорий книг, адресов покупателей, оплата заказов через `Stripe`, а так же логин, регистрация, сброс пароля и верификация аккаунта с помощью `FastAPI-Users` и отложенных задач. `70%` логики покрыты тестами `pytest` (согласно `pytest-cov`).
