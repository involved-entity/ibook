# iBook
__Backend__ часть для книжного маркетплейса `ibook`, написаная на современном асинхронном `FastAPI`. Так же используются __PostgreSQL, Redis, RabbitMQ, Celery, Alembic, SQLAlchemy, pytest, gunicorn, Docker, Prometheus, Grafana, Sentry__. Дополнительно проект настроен на использование `Stripe` для оплаты заказов на книги.
## Установка
```bash
git clone https://github.com/involved-entity/ibook
cd ibook
docker-compose up
```
Проект будет запущен в продакшен режиме на `http://localhost`:
1. `http://localhost/api` - API
2. `http://localhost/docs` - OpenAPI документация
3. `http://localhost:3000` - Grafana (admin : admin)
4. `http://localhost:5050` - pgAdmin (admin@example.com : admin123)
## Функционал
Пользователи имеют роли и соответствующие ролям права:
1. `ADMIN`
2. `SELLER`
3. `CUSTOMER`  

Реализована логика:
1. Заказов книг
2. Oтзывов на книги, 
3. Kатегорий книг
4. Aдресов покупателей
5. Oплаты заказов через `Stripe`
6. Логин, регистрация, сброс пароля и верификация аккаунта с помощью `FastAPI-Users` и отложенных задач.   

`70%` логики покрыты тестами `pytest` (согласно `pytest-cov`). Так же используется технология кэширования.
