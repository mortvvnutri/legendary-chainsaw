from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from db_connect import get_connection
from routers.auth import decode_token
from datetime import datetime
import psycopg2
from typing import List

router = APIRouter(prefix="/admin/tasks", tags=["admin-tasks"])

security = HTTPBearer()

@router.get("/list", responses={
    200: {"description": "List of all tasks"},
    401: {"description": "Unauthorized"},
    500: {"description": "Internal server error"},
    503: {"description": "Database unavailable"}
})
def list_tasks(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can view tasks")

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT task_id, qwestion, answer, created_at FROM task ORDER BY task_id")
        tasks = cur.fetchall()
        result = []
        for task in tasks:
            result.append({
                "task_id": task[0],
                "question": task[1],
                "answer": task[2],
                "created_at": task[3].isoformat()
            })
        return result

    except psycopg2.OperationalError:
        raise HTTPException(status_code=503, detail="Database connection failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@router.get("/list_short", responses={
    200: {"description": "Short list of all tasks (no answers)"},
    401: {"description": "Unauthorized"},
    500: {"description": "Internal server error"},
    503: {"description": "Database unavailable"}
})
def list_tasks_short(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can view tasks")

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT task_id, qwestion, created_at FROM task ORDER BY task_id")
        tasks = cur.fetchall()
        return [
            {
                "task_id": t[0],
                "question": t[1],
                "created_at": t[2].isoformat()
            } for t in tasks
        ]
    except psycopg2.OperationalError:
        raise HTTPException(status_code=503, detail="Database connection failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@router.get("/solution", responses={
    200: {"description": "Single solution by team and task"},
    400: {"description": "Missing team_id or task_id"},
    401: {"description": "Unauthorized"},
    404: {"description": "Solution not found"},
    500: {"description": "Internal server error"},
    503: {"description": "Database unavailable"}
})
def get_solution_by_team_and_task(
    team_id: int,
    task_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can access solutions")

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT solution_id, condition, answer, sent_at, approved_at
            FROM solution
            WHERE team_id = %s AND task_id = %s
        """, (team_id, task_id))
        row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Solution not found")

        return {
            "solution_id": row[0],
            "status": row[1],
            "answer": row[2],
            "sent_at": row[3].isoformat(),
            "approved_at": row[4].isoformat() if row[4] else None
        }

    except psycopg2.OperationalError:
        raise HTTPException(status_code=503, detail="Database connection failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

class TaskIdsInput(BaseModel):
    task_ids: List[int]

@router.get("/team_solutions", responses={
    200: {"description": "Solutions by team"},
    401: {"description": "Unauthorized"},
    400: {"description": "Missing team_id"},
    500: {"description": "Internal server error"},
    503: {"description": "Database unavailable"}
})
def get_team_solutions(
    team_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can view solutions")

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT solution_id, task_id, condition, answer, sent_at, approved_at
            FROM solution
            WHERE team_id = %s
            ORDER BY task_id
        """, (team_id,))
        rows = cur.fetchall()
        return [
            {
                "solution_id": r[0],
                "task_id": r[1],
                "status": r[2],
                "answer": r[3],
                "sent_at": r[4].isoformat(),
                "approved_at": r[5].isoformat() if r[5] else None
            } for r in rows
        ]
    except psycopg2.OperationalError:
        raise HTTPException(status_code=503, detail="Database connection failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@router.get("/team_solutions_short", responses={
    200: {"description": "Solutions by team (short, no answer)"},
    401: {"description": "Unauthorized"},
    400: {"description": "Missing team_id"},
    500: {"description": "Internal server error"},
    503: {"description": "Database unavailable"}
})
def get_team_solutions_short(
    team_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can view solutions")

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT solution_id, task_id, condition, sent_at, approved_at
            FROM solution
            WHERE team_id = %s
            ORDER BY task_id
        """, (team_id,))
        rows = cur.fetchall()
        return [
            {
                "solution_id": r[0],
                "task_id": r[1],
                "status": r[2],
                "sent_at": r[3].isoformat(),
                "approved_at": r[4].isoformat() if r[4] else None
            } for r in rows
        ]
    except psycopg2.OperationalError:
        raise HTTPException(status_code=503, detail="Database connection failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@router.get("/task_solutions", responses={
    200: {"description": "Solutions by task"},
    401: {"description": "Unauthorized"},
    400: {"description": "Missing task_id"},
    500: {"description": "Internal server error"},
    503: {"description": "Database unavailable"}
})
def get_task_solutions(
    task_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can view solutions")

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT solution_id, team_id, condition, answer, sent_at, approved_at
            FROM solution
            WHERE task_id = %s
            ORDER BY team_id
        """, (task_id,))
        rows = cur.fetchall()
        return [
            {
                "solution_id": r[0],
                "team_id": r[1],
                "status": r[2],
                "answer": r[3],
                "sent_at": r[4].isoformat(),
                "approved_at": r[5].isoformat() if r[5] else None
            } for r in rows
        ]
    except psycopg2.OperationalError:
        raise HTTPException(status_code=503, detail="Database connection failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@router.get("/task_solutions_short", responses={
    200: {"description": "Solutions by task (short, no answer)"},
    401: {"description": "Unauthorized"},
    400: {"description": "Missing task_id"},
    500: {"description": "Internal server error"},
    503: {"description": "Database unavailable"}
})
def get_task_solutions_short(
    task_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can view solutions")

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT solution_id, team_id, condition, sent_at, approved_at
            FROM solution
            WHERE task_id = %s
            ORDER BY team_id
        """, (task_id,))
        rows = cur.fetchall()
        return [
            {
                "solution_id": r[0],
                "team_id": r[1],
                "status": r[2],
                "sent_at": r[3].isoformat(),
                "approved_at": r[4].isoformat() if r[4] else None
            } for r in rows
        ]
    except psycopg2.OperationalError:
        raise HTTPException(status_code=503, detail="Database connection failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

class TaskInput(BaseModel):
    question: str
    answer: str

@router.post("/load", responses={
    201: {"description": "Task successfully created"},
    401: {"description": "Unauthorized"},
    500: {"description": "Internal server error"},
    503: {"description": "Database unavailable"}
})
def load_task(
    data: TaskInput,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can load tasks")

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT MAX(task_id) FROM task")
        max_id = cur.fetchone()[0] or 0
        new_id = max_id + 1

        cur.execute("""
            INSERT INTO task (task_id, answer, qwestion, created_at)
            VALUES (%s, %s, %s, NOW())
        """, (new_id, data.answer, data.question))

        conn.commit()
        return {"message": "Task successfully created", "task_id": new_id}

    except psycopg2.OperationalError:
        raise HTTPException(status_code=503, detail="Database connection failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

class AnswerUpdateRequest(BaseModel):
    team_id: int
    task_id: int

@router.post("/answers/approve", responses={
    200: {"description": "Solution approved"},
    401: {"description": "Unauthorized"},
    404: {"description": "Solution not found"},
    500: {"description": "Internal server error"},
    503: {"description": "Database unavailable"}
})
def approve_solution(
    data: AnswerUpdateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can approve solutions")

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT 1 FROM solution WHERE team_id = %s AND task_id = %s
        """, (data.team_id, data.task_id))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Solution not found")

        cur.execute("""
            UPDATE solution
            SET condition = 'approve', approved_at = NOW()
            WHERE team_id = %s AND task_id = %s
        """, (data.team_id, data.task_id))

        conn.commit()
        return {"message": "Solution approved"}
    except psycopg2.OperationalError:
        raise HTTPException(status_code=503, detail="Database connection failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()


@router.post("/answers/reject", responses={
    200: {"description": "Solution rejected"},
    401: {"description": "Unauthorized"},
    404: {"description": "Solution not found"},
    500: {"description": "Internal server error"},
    503: {"description": "Database unavailable"}
})
def reject_solution(
    data: AnswerUpdateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can reject solutions")

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT 1 FROM solution WHERE team_id = %s AND task_id = %s
        """, (data.team_id, data.task_id))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Solution not found")

        cur.execute("""
            UPDATE solution
            SET condition = 'reject', approved_at = NULL
            WHERE team_id = %s AND task_id = %s
        """, (data.team_id, data.task_id))

        conn.commit()
        return {"message": "Solution rejected"}
    except psycopg2.OperationalError:
        raise HTTPException(status_code=503, detail="Database connection failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@router.delete("/remove", responses={
    200: {"description": "Task successfully deleted"},
    401: {"description": "Unauthorized"},
    404: {"description": "Task not found"},
    500: {"description": "Internal server error"},
    503: {"description": "Database unavailable"}
})
def remove_task(
    task_id: int = Query(..., description="ID задачи для удаления"),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can delete tasks")

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Проверим, существует ли задача
        cur.execute("SELECT COUNT(*) FROM task WHERE task_id = %s", (task_id,))
        if cur.fetchone()[0] == 0:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

        # Удалим решение, если оно есть (внешний ключ от solution к task)
        cur.execute("DELETE FROM solution WHERE task_id = %s", (task_id,))
        cur.execute("DELETE FROM task WHERE task_id = %s", (task_id,))
        conn.commit()

        return {"message": f"Task with ID {task_id} successfully deleted"}

    except psycopg2.OperationalError:
        raise HTTPException(status_code=503, detail="Database connection failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@router.delete("/answers/remove", responses={
    200: {"description": "Solution successfully deleted"},
    401: {"description": "Unauthorized"},
    404: {"description": "Solution not found"},
    500: {"description": "Internal server error"},
    503: {"description": "Database unavailable"}
})
def remove_solution(
    team_id: int,
    task_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can remove solutions")

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Проверяем наличие решения
        cur.execute("""
            SELECT 1 FROM solution WHERE team_id = %s AND task_id = %s
        """, (team_id, task_id))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Solution not found")

        # Удаляем решение
        cur.execute("""
            DELETE FROM solution WHERE team_id = %s AND task_id = %s
        """, (team_id, task_id))
        conn.commit()

        return {"message": f"Solution for team {team_id} and task {task_id} deleted"}

    except psycopg2.OperationalError:
        raise HTTPException(status_code=503, detail="Database connection failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@router.delete("/clear", responses={
    200: {"description": "All tasks and solutions successfully deleted"},
    401: {"description": "Unauthorized"},
    500: {"description": "Internal server error"},
    503: {"description": "Database unavailable"}
})
def clear_tasks(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can clear tasks")

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Удаляем сначала все решения, затем все задачи
        cur.execute("DELETE FROM solution")
        cur.execute("DELETE FROM task")
        conn.commit()

        return {"message": "All tasks and solutions successfully deleted"}

    except psycopg2.OperationalError:
        raise HTTPException(status_code=503, detail="Database connection failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@router.delete("/answers/clear", responses={
    200: {"description": "All solutions successfully deleted"},
    401: {"description": "Unauthorized"},
    500: {"description": "Internal server error"},
    503: {"description": "Database unavailable"}
})
def clear_all_solutions(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can clear solutions")

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM solution")
        conn.commit()

        return {"message": "All solutions successfully deleted"}

    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()
