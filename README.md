# praktika_rinh_humsters_1cource
=======
# Backend: Сервис проведения конкурса по искусственному интеллекту
# V0.3 | FULL API: Auth, Tasks, Answers, Dashboard, Admin
## 📌 Описание

Серверная часть проекта реализует:
- авторизацию команды и администратора
- регистрацию новых команд
- выдачу и загрузку задач
- проверку решений и модерацию админом
- публичную дашборд-аналитику в реальном времени
- отслеживание статуса подключения пользователя

---

## 🚀 Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://gitverse.ru/nahya/praktika_rinh_humsters_1cource.git
cd your-repo-name 
```

### 2. Создание виртуального окружения и установка зависимостей

```bash
python -m venv venv
venv\Scripts\activate      # Windows
# или
source venv/bin/activate  # Linux/macOS

pip install -r requirements.txt
```

---

### 3. Настройка переменных окружения

Создайте файл `.env` в корне проекта со следующим содержимым:

```
POSTGRES_DB=contestdb # Название базы данных 
POSTGRES_USER=postgres # Имя пользователя PSQL 
POSTGRES_PASSWORD=yourpassword # Пароль пользователя PSQL
POSTGRES_HOST=localhost # Адрес PSQL сервера
POSTGRES_PORT=5432 # Порт PSQL сервера
JWT_EXP_HOURS=336 # Время жизни JWT токена
```

---

### 4. Создание базы данных

1. Создайте пустую базу данных `contestdb` вручную через pgAdmin или psql:

```sql
CREATE DATABASE contestdb;
```

2. Запустите скрипт для создания таблиц:

```bash
cd toys
python create_db.py
```

---

### 5. Создание администратора

Запустите утилиту генерации соли и хеша:

```bash
python generator_salt_hash.py # Укажите внутри исполняемого файла пароль
```

Скопируйте `salt` и `hash`, затем вставьте в БД командой:

```sql
INSERT INTO teams (team_id, updated_at, login, password_hash, password_salt, created_at)
VALUES (1, NOW(), 'admin', 'HASH_ИЗ_СКРИПТА', 'SALT_ИЗ_СКРИПТА', NOW());
```

---

### 6. Запуск сервера

```bash
uvicorn main:app --reload
```

Сервер будет доступен по адресу: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🧪 Доступные запросы

📂 ping
| Метод | Путь               | Описание |
| ----- | ------------------ | -------- |
| `GET` | `/ping/`           | Ping     |
| `GET` | `/ping/bd_connect` | Ping Db  |

📂 auth
| Метод  | Путь                | Описание      |
| ------ | ------------------- | ------------- |
| `POST` | `/auth/login`       | Team Login    |
| `POST` | `/auth/login/admin` | Admin Login   |
| `POST` | `/auth/register`    | Register Team |

📂 admin-tasks
| Метод    | Путь                                | Описание                      |
| -------- | ----------------------------------- | ----------------------------- |
| `GET`    | `/admin/tasks/list`                 | List Tasks                    |
| `GET`    | `/admin/tasks/list_short`           | List Tasks Short              |
| `GET`    | `/admin/tasks/solution`             | Get Solution By Team And Task |
| `GET`    | `/admin/tasks/team_solutions`       | Get Team Solutions            |
| `GET`    | `/admin/tasks/team_solutions_short` | Get Team Solutions Short      |
| `GET`    | `/admin/tasks/task_solutions`       | Get Task Solutions            |
| `GET`    | `/admin/tasks/task_solutions_short` | Get Task Solutions Short      |
| `POST`   | `/admin/tasks/load`                 | Load Task                     |
| `POST`   | `/admin/tasks/answers/approve`      | Approve Solution              |
| `POST`   | `/admin/tasks/answers/reject`       | Reject Solution               |
| `DELETE` | `/admin/tasks/remove`               | Remove Task                   |
| `DELETE` | `/admin/tasks/answers/remove`       | Remove Solution               |
| `DELETE` | `/admin/tasks/clear`                | Clear Tasks                   |
| `DELETE` | `/admin/tasks/answers/clear`        | Clear All Solutions           |

📂 team-tasks
| Метод  | Путь                      | Описание               |
| ------ | ------------------------- | ---------------------- |
| `GET`  | `/team/tasks/get_task`    | Get Next Task For Team |
| `POST` | `/team/tasks/answer_load` | Answer Load            |

📂 dashboard

| Метод | Путь                  | Описание                 |
| ----- | --------------------- | ------------------------ |
| `GET` | `/dashboard/`         | Get Dashboard            |

📂 default

| Метод | Путь | Описание |
| ----- | ---- | -------- |
| `GET` | `/`  | Root     |

---

## 📁 Структура проекта

<details>
<summary>Показать</summary>

```
.
.env (example)
README.md
main.py
db_connect.py
requirements.txt

routers/
├──team
|  ├──tasks.py
|  └──ws_status.py
├──admin
|  └──tasks.py
├── auth.py
├── dashboard.py
└── ping.py

toys/
├── create_db.py
└── generator_salt_hash.py
```

</details>

---

## 📄 Лицензия

Проект создан в рамках учебной практики. Автор кейса: Щербаков С.М.

