from fastapi import APIRouter, HTTPException
from db_connect import get_connection
import psycopg2
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/", responses={
    200: {"description": "Dashboard with team statuses and task results"},
    500: {"description": "Internal server error"},
    503: {"description": "Database unavailable"}
})
def get_dashboard():
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Получаем команды
        cur.execute("SELECT team_id, login FROM teams ORDER BY team_id")
        teams = cur.fetchall()

        # Получаем все задания
        cur.execute("SELECT task_id FROM task ORDER BY task_id")
        task_ids = [row[0] for row in cur.fetchall()]

        # Все решения
        cur.execute("SELECT team_id, task_id, condition, sent_at, approved_at FROM solution")
        solutions_raw = cur.fetchall()

        # Последняя активность для определения подключения
        cur.execute("SELECT team_id, MAX(sent_at) FROM solution GROUP BY team_id")
        now = datetime.now(timezone.utc)
        activity = {
            row[0]: "подключена" if now - row[1] <= timedelta(minutes=2) else "отключена"
            for row in cur.fetchall()
        }

        # Решения по командам и задачам
        solutions = {}
        for team_id, task_id, condition, _, _ in solutions_raw:
            if team_id not in solutions:
                solutions[team_id] = {}
            if condition == "approve":
                status = "зачет"
            elif condition == "verification":
                status = "отправлен"
            else:
                status = "отклонено"
            solutions[team_id][task_id] = status

        # Формируем итог
        result = []
        for team_id, login in teams:
            row = {
                "team_name": login,
                "status": activity.get(team_id, "отключена"),
                "files": {
                    str(task_id): solutions.get(team_id, {}).get(task_id, "")
                    for task_id in task_ids
                }
            }
            result.append(row)

        return result

    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()
