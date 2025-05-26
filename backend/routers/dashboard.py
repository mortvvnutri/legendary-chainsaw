from fastapi import APIRouter, HTTPException
from db_connect import get_connection
import asyncpg

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/", responses={
    200: {"description": "Dashboard with team statuses and task results"},
    500: {"description": "Internal server error"},
    503: {"description": "Database unavailable"}
})
async def get_dashboard():
    try:
        conn = await get_connection()

        # Получаем команды, исключая админа
        teams = await conn.fetch("SELECT team_id, login, status FROM teams WHERE login != 'admin' ORDER BY team_id")

        # Получаем все задания
        task_rows = await conn.fetch("SELECT task_id FROM task ORDER BY task_id")
        task_ids = [row["task_id"] for row in task_rows]

        # Получаем все решения
        solutions_raw = await conn.fetch("SELECT team_id, task_id, condition FROM solution")

        # Обрабатываем статусы решений
        solutions = {}
        for row in solutions_raw:
            team_id = row["team_id"]
            task_id = row["task_id"]
            condition = row["condition"]

            if team_id not in solutions:
                solutions[team_id] = {}

            if condition == "approve":
                status = "зачет"
            elif condition == "verification" or condition == "sent":
                status = "отправлен"
            else:
                status = "отклонено"

            solutions[team_id][task_id] = status

        # Собираем дашборд
        result = []
        for row in teams:
            team_id = row["team_id"]
            login = row["login"]
            online_status = row["status"]

            result.append({
                "team_name": login,
                "status": "подключена" if online_status == "online" else "отключена",
                "files": {
                    str(task_id): solutions.get(team_id, {}).get(task_id, "")
                    for task_id in task_ids
                }
            })

        return result

    except asyncpg.PostgresError as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        if 'conn' in locals():
            await conn.close()
