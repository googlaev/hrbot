# Архитектура проекта

Данный документ описывает структуру проекта, его ключевые модули и логику организации кода. Проект построен по принципам чистой архитектуры (Clean Architecture) и разделён на уровни: **adapters**, **app**, **domain**, **infra**, **tests**.

---

## Корневая структура

```
D:.
├── .env                 # Переменные окружения
├── .gitignore           # Игнорируемые файлы Git
├── pytest.ini           # Конфигурация Pytest
├── README.md
├── examples             # Примеры
├── data/                # База данных
├── docs/                # Документация
├── logs/                # Логи приложения
├── src/                 # Исходный код
└── tests/               # Тесты
```

---

## `data/`

**app.db** — SQLite база данных, используемая приложением.

---

## `docs/`

Документы, связанные с архитектурой, процессами разработки и спецификацией вопросов.

---

## `logs/`

Логи работы приложения и ошибок:

* `app.log`
* `app_errors.log`

---

# `src/` — основной код проекта

Проект построен по слоям:

* **domain** — сущности, бизнес‑правила
* **app** — use-case слои, DTO, порты
* **adapters** — реализация портов, UI, интеграции
* **infra** — инфраструктура (БД, логгеры, телеграм‑бот)

---

## 1. `src/domain/` — предметная область

Здесь — чистые модели, ядро бизнес‑логики.

### entities/

* **quiz_entity.py** — модель тестов
* **user.py** — модель пользователя

### enums/

* **user_role.py** — роли пользователей (admin, user)

### exceptions/

Исключения доменного уровня.

---

## 2. `src/app/` — прикладной слой (Application Layer)

Содержит use-cases, DTO и абстракции.

### dtos/

* **quiz.py** — DTO для тестов
* **tg_auth_dto.py** — DTO для авторизации

### ports/

#### outbound

Абстракции, которые реализуют адаптеры:

* excel_parser_port.py
* logger_port.py

##### repositories/

Порты для работы с БД:

* quiz_repo_port.py
* telegram_auth_repo_port.py
* users_repo_port.py

### use_cases/

* **add_quiz_from_excel.py** — загрузка тестов из Excel
* **auth_by_telegram.py** — авторизация пользователя
* **check_admin_access.py** — проверка прав администратора

### app_actions.py

* Фасад для действий приложения.

---

## 3. `src/adapters/` — реализация портов (входные/выходные адаптеры)

### inbound/telegram_ui/

Реализация пользовательского интерфейса через Telegram‑бота.

#### handlers/

* **admin_handlers.py** — обработчики для админов
* **user_handlers.py** — обработчики пользователей

#### filters/

Фильтры для aiogram:

* admin_filter.py
* user_filter.py

#### middlewares/

* user_auth_middleware.py — middleware авторизации

### outbound/

#### parsers/

* **excel_parser.py** — загрузка и парсинг Excel

#### repositories/

* **quiz_repo.py** — реализация хранилища тестов
* **telegram_auth_repo.py** — реализация авторизации
* **users_repo.py** — работа с пользователями

---

## 4. `src/infra/` — инфраструктура

### database/

* **setup.py** — настройка БД
* **sqlite_db.py** — обёртка над SQLite

### telegram/

* **bot.py** — инициализация и запуск бота

### logger.py

Настройка и конфигурация логирования.

### tz_clock.py

Провайдер времени.

---

# `tests/` — тесты

### parsers/excel/

* **test_excel_parcer.py** — тестирование Excel‑парсера
* **conftest.py** — фикстуры для тестов

---

# Краткая логика архитектуры

* **domain** содержит неизменяемые бизнес‑правила и модели.
* **app** формирует use‑cases(scenarios), определяет контракты.
* **adapters** реализуют внешние интерфейсы (Telegram UI, БД, парсеры).
* **infra** отвечает за реализацию технических деталей — БД, логгирование.

Подход обеспечивает независимость домена от фреймворков и позволяет легко менять интерфейсы и технологии.

---