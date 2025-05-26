from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from routers.auth import decode_token
from db_connect import get_connection
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
import json

router = APIRouter(prefix="/team/tasks", tags=["team-tasks"])
security = HTTPBearer()

last_call_time = {}

@router.get("/get_task")
async def get_next_task_for_team(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    prev_task_id: int = Query(None, description="ID предыдущей задачи (для запроса следующей)")
):
    token = credentials.credentials
    payload = await decode_token(token)

    if payload.get("role") != "team":
        raise HTTPException(status_code=401, detail="Only teams can access this endpoint")

    team_id = payload["team_id"]
    now = datetime.now(timezone.utc)

    if team_id in last_call_time:
        delta = now - last_call_time[team_id]
        if delta < timedelta(seconds=30):
            raise HTTPException(
                status_code=429,
                detail=f"Request allowed once every 30 seconds. Please wait {30 - int(delta.total_seconds())} sec."
            )

    conn = await get_connection()
    try:
        viewed: list = await conn.fetchval("SELECT viewed_tasks FROM teams WHERE team_id = $1", team_id) or []

        if prev_task_id is not None:
            row = await conn.fetchrow(
                "SELECT task_id, qwestion FROM task WHERE task_id > $1 ORDER BY task_id LIMIT 1",
                prev_task_id
            )
            if not row:
                raise HTTPException(status_code=404, detail="No more tasks found")

            task_id, question = row["task_id"], row["qwestion"]

            max_id = await conn.fetchval("SELECT MAX(solution_id) FROM solution") or 0
            new_solution_id = max_id + 1

            await conn.execute("""
                INSERT INTO solution (solution_id, condition, answer, sent_at, approved_at, team_id, task_id)
                VALUES ($1, 'sent', '{}'::jsonb, NOW(), NULL, $2, $3)
            """, new_solution_id, team_id, task_id)

            if task_id not in viewed:
                await conn.execute("""
                    UPDATE teams SET viewed_tasks = array_append(viewed_tasks, $1)
                    WHERE team_id = $2
                """, task_id, team_id)

            last_call_time[team_id] = now
            return {"task_id": task_id, "question": question}

        else:
            # Получаем статусы всех решений этой команды
            solution_map = {
                r["task_id"]: r["condition"]
                for r in await conn.fetch("""
                    SELECT task_id, condition
                    FROM solution
                    WHERE team_id = $1
                    ORDER BY sent_at DESC
                """, team_id)
            }

            # Просмотренные задачи
            viewed_rows = await conn.fetch(
                "SELECT task_id, qwestion FROM task WHERE task_id = ANY($1::bigint[]) ORDER BY task_id",
                viewed
            )

            response = []

            for r in viewed_rows:
                task_id = r["task_id"]
                response.append({
                    "task_id": task_id,
                    "question": r["qwestion"],
                    "status": solution_map.get(task_id, "")
                })

            # Новая задача
            new_row = await conn.fetchrow(
                "SELECT task_id, qwestion FROM task WHERE task_id != ALL($1::bigint[]) ORDER BY task_id LIMIT 1",
                viewed
            )

            if new_row:
                new_task_id = new_row["task_id"]
                response.append({
                    "task_id": new_task_id,
                    "question": new_row["qwestion"],
                    "status": solution_map.get(new_task_id, "")
                })

                max_id = await conn.fetchval("SELECT MAX(solution_id) FROM solution") or 0
                new_solution_id = max_id + 1

                await conn.execute("""
                    INSERT INTO solution (solution_id, condition, answer, sent_at, approved_at, team_id, task_id)
                    VALUES ($1, 'sent', '{}'::jsonb, NOW(), NULL, $2, $3)
                """, new_solution_id, team_id, new_task_id)

                await conn.execute("""
                    UPDATE teams SET viewed_tasks = array_append(viewed_tasks, $1)
                    WHERE team_id = $2
                """, new_task_id, team_id)

            if not response:
                raise HTTPException(status_code=404, detail="Все задачи просмотрены")

            last_call_time[team_id] = now
            return {"tasks": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        await conn.close()



# ✅ Answer model
class SolutionInput(BaseModel):
    task_id: int
    answer: Dict[str, Any] = Field(..., description='Должен содержать ключ "selections"')

@router.post("/answer_load", responses={
    201: {"description": "Solution successfully submitted"},
    400: {"description": "Task not found or invalid input"},
    401: {"description": "Unauthorized"},
    409: {"description": "Solution already submitted"},
    500: {"description": "Internal server error"},
    503: {"description": "Database unavailable"}
})
async def answer_load(
    data: SolutionInput,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = await decode_token(token)

    if payload.get("role") != "team":
        raise HTTPException(status_code=401, detail="Only teams can submit answers")

    team_id = payload["team_id"]

    try:
        conn = await get_connection()

        task_exists = await conn.fetchval("SELECT 1 FROM task WHERE task_id = $1", data.task_id)
        if not task_exists:
            raise HTTPException(status_code=400, detail="Task not found")

        existing = await conn.fetchrow("""
            SELECT condition FROM solution
            WHERE team_id = $1 AND task_id = $2
            ORDER BY sent_at DESC LIMIT 1
        """, team_id, data.task_id)
        if existing and existing["condition"] != "sent":
            raise HTTPException(status_code=409, detail="Solution already submitted")

        # Валидация
        if not isinstance(data.answer, dict) or "selections" not in data.answer:
            raise HTTPException(status_code=400, detail='Answer must contain "selections" field')
        if not isinstance(data.answer["selections"], list):
            raise HTTPException(status_code=400, detail='"selections" must be a list')

        max_id = await conn.fetchval("SELECT MAX(solution_id) FROM solution") or 0
        new_id = max_id + 1

        await conn.execute("""
            INSERT INTO solution (solution_id, condition, answer, sent_at, approved_at, team_id, task_id)
            VALUES ($1, 'verification', $2::jsonb, NOW(), NULL, $3, $4)
        """, new_id, json.dumps(data.answer), team_id, data.task_id)

        return {"message": "Solution successfully submitted", "solution_id": new_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        await conn.close()
