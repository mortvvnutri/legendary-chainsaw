from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from routers.auth import decode_token
from db_connect import get_connection
from datetime import datetime, timedelta, timezone
import psycopg2

router = APIRouter(prefix="/team/tasks", tags=["team-tasks"])
security = HTTPBearer()

last_call_time = {}

@router.get("/get_task", responses={
    200: {"description": "Next task for team"},
    401: {"description": "Unauthorized"},
    429: {"description": "Too many requests"},
    404: {"description": "No tasks found"},
    500: {"description": "Internal server error"},
    503: {"description": "Database unavailable"}
})
def get_next_task_for_team(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("role") != "team":
        raise HTTPException(status_code=401, detail="Only teams can access this endpoint")

    team_id = payload["team_id"]

    now = datetime.now(timezone.utc)
    if team_id in last_call_time:
        delta = now - last_call_time[team_id]
        if delta < timedelta(seconds=30):
            raise HTTPException(status_code=429, detail=f"Request allowed once every 30 seconds. Please wait {30 - int(delta.total_seconds())} sec.")

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT task_id, qwestion FROM task ORDER BY task_id LIMIT 1")
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="No tasks found")
        task_id, question = row

        last_call_time[team_id] = now

        return {
            "task_id": task_id,
            "question": question
        }

    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

class SolutionInput(BaseModel):
    task_id: int
    answer: str

@router.post("/answer_load", responses={
    201: {"description": "Solution successfully submitted"},
    400: {"description": "Task not found or invalid input"},
    401: {"description": "Unauthorized"},
    409: {"description": "Solution already submitted"},
    500: {"description": "Internal server error"},
    503: {"description": "Database unavailable"}
})
def answer_load(
    data: SolutionInput,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("role") != "team":
        raise HTTPException(status_code=401, detail="Only teams can submit answers")

    team_id = payload["team_id"]

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM task WHERE task_id = %s", (data.task_id,))
        if cur.fetchone() is None:
            raise HTTPException(status_code=400, detail="Task not found")

        cur.execute("SELECT 1 FROM solution WHERE task_id = %s AND team_id = %s", (data.task_id, team_id))
        if cur.fetchone():
            raise HTTPException(status_code=409, detail="Solution already submitted")

        cur.execute("SELECT MAX(solution_id) FROM solution")
        max_id = cur.fetchone()[0] or 0
        new_id = max_id + 1

        cur.execute("""
            INSERT INTO solution (solution_id, condition, answer, sent_at, approved_at, team_id, task_id)
            VALUES (%s, %s, %s, NOW(), NULL, %s, %s)
        """, (new_id, 'verification', data.answer, team_id, data.task_id))

        conn.commit()
        return {"message": "Solution successfully submitted", "solution_id": new_id}

    except psycopg2.OperationalError:
        raise HTTPException(status_code=503, detail="Database connection failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()


