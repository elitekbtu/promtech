# Backend Technical Documentation — GidroAtlas API

## 1. Project Overview

**GidroAtlas Backend** — FastAPI-based water resource management system with AI-powered features:

Backend provides:

- Water object management with priority-based inspection system
- User authentication and Face ID verification
- Agentic RAG system powered by LangGraph and Google Gemini
- Role-based access control (guest/expert)
- RESTful API endpoints with Russian language support
- Passport document management and analysis
- Vector database integration for semantic search

---

## 2. Goals and Scope

### 2.1 Goals

- Manage water resources across Kazakhstan with geospatial data
- Provide priority-based inspection system for water objects
- Implement secure authentication with Face ID verification
- Enable role-based access (guest can view, expert can manage priorities)
- Deliver AI-powered query processing via RAG system
- Support passport document upload and analysis

### 2.2 Backend Responsibilities

- REST API (FastAPI, JSON) with Russian language support
- User authentication and authorization (JWT)
- Face ID verification and matching (DeepFace)
- Water object CRUD operations with filtering/sorting
- Priority calculation based on technical condition and passport age
- Database access with PostgreSQL
- AI-powered query processing via RAG system
- Integration with Google Gemini and vector databases
- File uploads (avatars, passport PDFs)

---

## 3. System Architecture

### 3.1 Architecture Style: Modular Monolith

The project uses **Modular Monolith** architecture. This provides clear domain separation and simplifies maintenance while keeping deployment simple.

**Folder Structure:**

```text
backend/
├── main.py               # FastAPI application entry point
├── database.py           # Database configuration (PostgreSQL)
├── requirements.txt      # Python dependencies
├── alembic/              # Database migrations
│   └── versions/
├── models/               # SQLAlchemy models
│   ├── user.py           # User model
│   ├── water_object.py   # WaterObject model
│   └── passport_text.py  # PassportText model
├── services/             # Business logic
│   ├── auth/             # Authentication services
│   ├── objects/          # Water object services
│   ├── priorities/       # Priority calculation
│   └── passports/        # Passport management
├── faceid/               # Face verification
│   ├── router.py
│   ├── service.py
│   └── schemas.py
├── rag_agent/            # Agentic RAG system
│   ├── config/
│   ├── routes/
│   ├── tools/
│   └── utils/
├── scripts/              # Data import and testing
│   ├── import_objects.py
│   ├── import_passports.py
│   ├── enrich_data.py
│   └── test_*.py
└── uploads/              # File storage
    ├── avatars/
    └── passports/
```

### 3.2 Core Components

- **FastAPI Backend**
  - Routes: `/api/auth`, `/api/objects`, `/api/priorities`, `/api/passports`, `/api/rag`, `/api/faceid`
  - OpenAPI/Swagger documentation at `/docs`
  - Runs in Docker container

- **PostgreSQL Database**
  - Supports models: User, WaterObject, PassportText
  - Migrations managed with Alembic
  - Runs via Docker Compose

- **File Storage**
  - Local folder/Docker volume with serving via `FILE_STORAGE_BASE_URL`
  - Stores passport PDFs and avatars
  - Backend stores only `pdf_url` references

- **Gemini API**
  - Primary LLM for chat/explain/search operations
  - Used through client wrapper in RAG system

- **Agentic RAG Layer**
  - Implemented as a separate module
  - Uses LangGraph for agent coordination
  - Agent processes queries, coordinates tools, and generates responses
  - Integrates with PostgreSQL for vector search
  - Assembles context and requests Gemini for final answer

### 3.3 Request Flows

1. **Maps and Lists**
   Frontend calls `/api/objects` → Backend filters/sorts in DB → Returns list with coordinates → Frontend renders map and table

2. **Object Details**
   `/api/objects/{id}` → Backend returns all fields + `pdf_url` → Frontend shows card and "Open Passport" button

3. **Prioritization**
   `/api/priorities/table` (expert only) → Backend returns table with `priority` scores

4. **AI / Agentic RAG**
   `/api/rag/query` → AI Agent:
   - Understands query
   - Decides whether to:
     - Filter SQL objects
     - Fetch passport text for objects/regions
   - Assembles context
   - Calls Gemini for final answer

2. **Карточка объекта**
   `/objects/{id}` → backend отдаёт все поля + `pdf_url` → фронт показывает карточку и кнопку “Открыть паспорт”.

3. **Приоритезация**
   `/priorities/table` (только `expert`) → backend отдаёт таблицу с `priority`.

4. **AI / Agentic RAG**
   `/ai/...` → **AI-агент**:

   - понимает запрос;
   - решает, нужно ли:

     - делать SQL-фильтр по объектам,
     - доставать текст паспорта объекта/регионов;

   - формирует контекст;
   - вызывает Gemini для финального ответа.

---

## 4. Data Model

### 4.1 User

Полностью соответствует ТЗ.

| Field         | Type     | Description              |
| ------------- | -------- | ------------------------ |
| id            | int/uuid | Уникальный идентификатор |
| login         | string   | Логин                    |
| password_hash | string   | Хэш пароля               |
| role          | enum     | `guest` / `expert`       |

### 4.2 WaterObject (Объект водного ресурса)

Тоже выровнено с ТЗ.

**Основные поля:**

- `id` — int/uuid, PK
- `name` — string, название
- `region` — string, область/регион
- `resource_type` — enum: `lake`, `canal`, `reservoir` (озеро/канал/водохранилище)
- `water_type` — enum: `fresh`, `non_fresh` (пресная/непресная)
- `fauna` — boolean, наличие фауны (да/нет)
- `passport_date` — date, дата паспорта
- `technical_condition` — int (1–5), техническое состояние
- `latitude` — float, широта
- `longitude` — float, долгота
- `pdf_url` — string, ссылка на PDF/скан паспорта
- `priority` — int, **основное поле приоритета по формуле ТЗ**
- **Дополнительно (не обязано ТЗ, но удобно):**

  - `priority_level` — enum: `high` / `medium` / `low` (текстовая категория для UI)
  - `osm_id` — bigint (если импортируем из OSM)

### 4.3 Priority Calculation

Формула ровно из ТЗ:

```text
PriorityScore = (6 - technical_condition) * 3 + passport_age_years
where passport_age_years = current_year - year(passport_date)
```

- В БД записывается в поле `priority` (int).
- `priority_level` получается простым mapping:

  - `priority >= 12` → `"high"`
  - `6 <= priority <= 11` → `"medium"`
  - `priority < 6` → `"low"`

Именно `priority` используется для сортировки/фильтрации, как в ТЗ “Приоритет обследования”.

### 4.4 Passports

Для хакатона:

- Храним только `pdf_url` в `WaterObject`.
- Для AI/RAG дополнительно делаем **вспомогательную таблицу `passport_texts`**:

| Field     | Type     | Description                         |
| --------- | -------- | ----------------------------------- |
| id        | int/uuid | PK                                  |
| object_id | FK       | Ссылка на `water_objects.id`        |
| text      | text     | Сплошной текст паспорта             |
| section   | string   | Логическая секция (phys, bio, etc.) |

Текст берём из файлов “Паспортизация” (физическая/биологическая характеристика, рыбопродуктивность и т.д.).

---

## 5. Authentication & Roles

### 5.1 Роли (строго по ТЗ)

- **Гость (`guest`)**:

  - доступ: **только просмотр** карты и объектов;
  - **не видит приоритеты и таблицу приоритизации**;
  - не может редактировать данные.

- **Эксперт (`expert`)**:

  - доступ ко всем данным: состояние, приоритеты, таблицы;
  - может открывать паспорта;
  - может использовать фильтры и поиск в полном объёме.

### 5.2 Auth Flow (минимальный)

- `POST /auth/login`:

  - принимает `login`, `password`;
  - возвращает JWT с полем `role`.

- `POST /auth/logout`:

  - фронт просто удаляет токен.

- Если токена нет → фронт работает в режиме гостя.

Backend:

- хранит пользователей в таблице `users`;
- при логине:

  - проверяет логин/пароль,
  - возвращает токен формата:

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer",
  "role": "expert"
}
```

---

## 6. API Design (основное + AI)

Все ответы в JSON, поддерживается пагинация и сортировка.

### 6.1 Auth

#### POST `/auth/login`

- **Описание:** простая авторизация по логину и паролю.
- **Body:**

```json
{
  "login": "expert1",
  "password": "secret"
}
```

- **Успех (200):** токен + роль.
- **Ошибка:** 401 при неверных данных.

#### POST `/auth/logout`

- **Описание:** логическое завершение сессии (фронт удаляет токен).

---

### 6.2 Объекты водных ресурсов

#### GET `/objects`

**Назначение:** список объектов с фильтрацией/поиском/сортировкой.

Поля фильтрации строго из ТЗ:

**Query params:**

- `page`: int, default 1
- `page_size`: int, default 20
- `region`: string (область)
- `resource_type`: `lake` / `canal` / `reservoir`
- `water_type`: `fresh` / `non_fresh`
- `has_fauna`: bool
- `passport_date_from`: date
- `passport_date_to`: date
- `technical_condition_min`: int
- `technical_condition_max`: int
- `search`: string — поиск по названию / метаданным (если есть)
- `priority_min`, `priority_max`: int (для эксперта)
- `priority_level`: `high` / `medium` / `low` (для эксперта)
- `sort_by`: одно из:

  - `name`, `region`, `resource_type`, `water_type`, `fauna`,
  - `passport_date`, `technical_condition`, `priority`

- `sort_order`: `asc` / `desc`

**Ответ:**

```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Бараккол",
      "region": "Улытауская область",
      "resource_type": "lake",
      "water_type": "non_fresh",
      "fauna": true,
      "passport_date": "2023-01-01",
      "technical_condition": 3,
      "latitude": 49.3147,
      "longitude": 67.2756,
      "pdf_url": "https://storage/.../barakkol.pdf",

      // поля, зависящие от роли:
      "priority": 14,
      "priority_level": "high"
    }
  ],
  "total": 123,
  "page": 1,
  "page_size": 20
}
```

**Различие по ролям:**

- `guest` → поля `priority` и `priority_level` **не включаются** в ответ;
- `expert` → поля приоритета включаются.

#### GET `/objects/{object_id}`

**Назначение:** карточка объекта. Содержит все поля из ТЗ.

**Ответ (эксперт):**

```json
{
  "id": "uuid",
  "name": "Бараккол",
  "region": "Улытауская область",
  "resource_type": "lake",
  "water_type": "non_fresh",
  "fauna": true,
  "passport_date": "2023-01-01",
  "technical_condition": 3,
  "latitude": 49.3147,
  "longitude": 67.2756,
  "pdf_url": "https://storage/.../barakkol.pdf",
  "priority": 14,
  "priority_level": "high"
}
```

**Для `guest`** те же поля, но без `priority` и `priority_level`.

#### GET `/objects/{object_id}/passport`

**Назначение:** метаданные паспорта.

**Ответ:**

```json
{
  "object_id": "uuid",
  "exists": true,
  "pdf_url": "https://storage/.../barakkol-passport.pdf"
}
```

Если данных нет:

```json
{
  "object_id": "uuid",
  "exists": false
}
```

---

### 6.3 Приоритезация

#### GET `/priorities/table` (только expert)

**Назначение:** таблица приоритезации объектов, как в ТЗ “Рабочий дашборд приоритезации”.

**Query params:**

- те же, что в `/objects` (region, resource_type, water_type, fauna, passport_date range, technical_condition, search);
- плюс:

  - `priority_min`, `priority_max`,
  - `priority_level`.

**Ответ:**

```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Камыстыкол",
      "region": "Улытауская область",
      "technical_condition": 5,
      "passport_date": "2018-01-01",
      "priority": 15,
      "priority_level": "high"
    }
  ],
  "total": 10
}
```

Роут защищён dependency `require_expert()`.

---

### 6.4 AI / Gemini Endpoints (Agentic RAG)

Все AI-эндпоинты используют **один сервисный слой** `GeminiAgentService`.

#### 6.4.1 POST `/ai/chat`

**Назначение:** общий чат по системе и объектам.

**Body:**

```json
{
  "query": "Какие водоемы с высоким приоритетом в Улытауском регионе?",
  "language": "ru"
}
```

**Agentic RAG flow:**

1. Агент анализирует запрос (внутренний prompt в Gemini типа “classify intent”).
2. Выбирает “инструменты”:

   - SQL-поиск в таблице `water_objects` по `region` + `priority='high'`;
   - при необходимости — загрузка паспортов этих объектов из `passport_texts`.

3. Собирает краткий контекст (название, приоритет, ключевые характеристики из паспортов).
4. Отправляет всё это в Gemini как system+user prompt и возвращает итоговый `answer`.

**Ответ:**

```json
{
  "answer": "В Улытауском регионе высокий приоритет имеют озера Бараккол, Коскол и Камыстыкол...",
  "objects": [
    { "id": "uuid1", "name": "Бараккол", "priority": 14 },
    { "id": "uuid2", "name": "Коскол", "priority": 13 }
  ]
}
```

#### 6.4.2 POST `/ai/objects/{object_id}/explain-priority`

**Назначение:** объяснение приоритета конкретного объекта.

**Body:**

```json
{
  "language": "ru"
}
```

**Agentic RAG flow:**

1. Агент достаёт объект из БД: `technical_condition`, `passport_date`, `priority`.

2. Достаёт текст паспорта из `passport_texts` (хотя бы несколько ключевых секций: физика, биология, рыбопродуктивность).

3. Формирует системный prompt:

   > “Ты инженер-гидробиолог. Объясни, почему приоритет обследования такой, опираясь на состояние (1–5), возраст паспорта и краткие характеристики водоёма.”

4. Передаёт в Gemini и возвращает ответ.

**Ответ:**

```json
{
  "object_id": "uuid",
  "priority": 14,
  "priority_level": "high",
  "explanation": "Приоритет высокий, так как техническое состояние оценено как 5 (близко к аварийному), паспорт обновлялся более 7 лет назад, а в паспорте описана высокая степень зарастания водоема..."
}
```

#### 6.4.3 POST `/ai/search`

**Назначение:** “умный” поиск по базе и паспортам естественным языком.

**Body:**

```json
{
  "query": "Озера с непресной водой и высокой рыбопродуктивностью в Улытауском районе",
  "language": "ru"
}
```

**Agentic RAG flow (упрощённый):**

1. Агент просит Gemini классифицировать запрос (какие поля, какие фильтры, какой регион).
2. Backend выполняет SQL-поиск по:

   - `resource_type = 'lake'`,
   - `water_type = 'non_fresh'`,
   - `region` ≈ "Улытауская".

3. Для найденных объектов достаёт текст паспортов и ищет в них ключевые слова (“рыбопродуктивность”, значения кг/га и т.п.).

   - На MVP этапе можно использовать просто `LIKE` по тексту паспорта.

4. Собирает небольшой JSON-контекст и просит Gemini:

   - отфильтровать самые релевантные объекты;
   - кратко их описать.

**Ответ:**

```json
{
  "results": [
    {
      "object_id": "uuid",
      "name": "Бараккол",
      "summary": "Непресное озеро, рыбопродуктивность около 60 кг/га, высокая степень зарастания."
    }
  ]
}
```

---

## 7. AI & Gemini Integration (Agentic RAG Module)

### 7.1 Обзор и Источник

В проекте используется продвинутая система **Agentic RAG**, основанная на **LangGraph**.
Исходный код референсной реализации находится в папке `backend/Agentic_rag`.

**Задача интеграции:**
Необходимо адаптировать этот код под архитектуру **Modular Monolith** и требования GidroAtlas.

### 7.2 Требования к адаптации (Refactoring)

1.  **Архитектура:**

    - Перенести логику из `backend/Agentic_rag` в модуль приложения (например, `app/modules/ai`).
    - Избавиться от `main.py` внутри RAG, интегрировав роуты в основной `FastAPI` app.

2.  **База данных:**

    - В референсе используется **SQLite** (`hacknu_rag.db`).
    - **Необходимо:** Перевести все хранилища (история чатов, векторный стор) на основной **PostgreSQL**.

3.  **Инструменты (Tools):**
    - Заменить общие инструменты на специфичные для GidroAtlas:
      - `search_water_objects` (SQL-фильтр по `WaterObject`).
      - `get_passport_content` (RAG по текстам паспортов).
      - `explain_priority_logic` (расчет приоритета).

### 7.3 Конфигурация

Через переменные окружения (дополняет основной `.env`):

- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `TAVILY_API_KEY` (если используется для внешнего поиска, иначе отключить).

### 7.4 Сервисный слой: `GeminiAgentService`

Этот слой теперь выступает фасадом над графом агентов (LangGraph).

Примерный интерфейс:

- `chat(query: str, user_role: str, language: str) -> ChatResponse`
- `explain_priority(object_id: str, language: str) -> ExplanationResponse`
- `semantic_search(query: str, language: str) -> SearchResponse`

Внутри:

- Вызов графа агентов (LangGraph);
- Инструменты (Tools):

  - `fetch_objects(filters)`;
  - `fetch_passport_text(object_id)`.

### 7.5 Prompt-шаблоны (упрощённо)

**System prompt (общий):**

> Ты — помощник по гидротехническим сооружениям Казахстана. У тебя есть таблица объектов и тексты паспортов, которые передаёт сервер. Отвечай структурировано, кратко, опираясь только на переданные данные. Если информации не хватает — честно скажи об этом.

**System prompt (объяснение приоритета):**

> Ты инженер-гидробиолог. Объясни, почему у объекта такой приоритет обследования. Используй его техническое состояние, возраст паспорта и краткие характеристики из паспорта (зарастание, рыбопродуктивность и т.п.). Объяснение — 2–4 предложения.

---

## 8. External Data Source (Seeder)

Чтобы не руками вбивать объекты, для хакатона достаточно:

- один небольшой скрипт `scripts/import_osm_water.py`, который:

  - берёт данные из Overpass/OSM по Казахстану (или конкретному региону),
  - создаёт записи `water_objects` (name, region, lat/lon, resource_type, water_type),
  - дальше вы вручную добавляете несколько “живых” объектов из файлов по паспортизации (Бараккол, Коскол, Камыстыкол и т.д.).

Это ускоряет старт и даёт реалистичный объём данных.

---

## 9. Configuration & Running

### 9.1 Environment variables

- `DATABASE_URL` — строка подключения к PostgreSQL.
- `SECRET_KEY` — секрет для JWT.
- `ACCESS_TOKEN_EXPIRE_MINUTES` — срок жизни токена.
- `GEMINI_API_KEY`, `GEMINI_MODEL`.
- `FILE_STORAGE_BASE_URL` — базовый URL для паспортов.

### 9.2 Запуск через Docker Compose (Рекомендуемый)

1. Создать файл `.env` с переменными окружения.
2. Запустить сборку и контейнеры:

```bash
docker-compose up --build
```

Приложение будет доступно по адресу `http://localhost:8000`.

### 9.3 Локальный запуск (ручной, используя uv)

1. Установить `uv` (если не установлен).
2. Установить зависимости:

```bash
uv sync
```

3. Применить миграции (если используете Alembic):

```bash
uv run alembic upgrade head
```

4. Запустить FastAPI:

```bash
uv run uvicorn app.main:app --reload
```

5. Открыть документацию:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

6. (Опционально) Запустить скрипт импорта OSM и добавить несколько паспортов в `passport_texts`.
