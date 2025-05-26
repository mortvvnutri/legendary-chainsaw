from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from db_connect import get_connection
from routers.auth import decode_token
from datetime import datetime
from typing import Dict, Any
import json

router = APIRouter(prefix="/admin/tasks", tags=["admin-tasks"])
security = HTTPBearer()


@router.get("/list")
async def list_tasks(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = await decode_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can view tasks")

    try:
        conn = await get_connection()
        rows = await conn.fetch("SELECT task_id, qwestion, answer, created_at FROM task ORDER BY task_id")
        return [{
            "task_id": row["task_id"],
            "question": row["qwestion"],
            "answer": row["answer"] if isinstance(row["answer"], dict) else json.loads(row["answer"]),
            "created_at": row["created_at"].isoformat()
        } for row in rows]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        await conn.close()


@router.get("/list_short")
async def list_tasks_short(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = await decode_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can view tasks")

    try:
        conn = await get_connection()
        rows = await conn.fetch("SELECT task_id, qwestion, created_at FROM task ORDER BY task_id")
        return [{
            "task_id": row["task_id"],
            "question": row["qwestion"],
            "created_at": row["created_at"].isoformat()
        } for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        await conn.close()


@router.get("/solution")
async def get_solution_by_team_and_task(
    team_id: int,
    task_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = await decode_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can access solutions")

    try:
        conn = await get_connection()
        row = await conn.fetchrow("""
            SELECT solution_id, condition, answer, sent_at, approved_at
            FROM solution
            WHERE team_id = $1 AND task_id = $2
        """, team_id, task_id)

        if not row:
            raise HTTPException(status_code=404, detail="Solution not found")

        return {
            "solution_id": row["solution_id"],
            "status": row["condition"],
            "answer": row["answer"] if isinstance(row["answer"], dict) else json.loads(row["answer"]),
            "sent_at": row["sent_at"].isoformat(),
            "approved_at": row["approved_at"].isoformat() if row["approved_at"] else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        await conn.close()

@router.get("/team_solutions")
async def get_team_solutions(
    team_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = await decode_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can view solutions")

    try:
        conn = await get_connection()
        rows = await conn.fetch("""
            SELECT solution_id, task_id, condition, answer, sent_at, approved_at
            FROM solution
            WHERE team_id = $1
            ORDER BY task_id
        """, team_id)

        return [{
            "solution_id": r["solution_id"],
            "task_id": r["task_id"],
            "status": r["condition"],
            "answer": r["answer"] if isinstance(r["answer"], dict) else json.loads(r["answer"]),
            "sent_at": r["sent_at"].isoformat(),
            "approved_at": r["approved_at"].isoformat() if r["approved_at"] else None
        } for r in rows]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        await conn.close()


@router.get("/team_solutions_short")
async def get_team_solutions_short(
    team_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = await decode_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can view solutions")

    try:
        conn = await get_connection()
        rows = await conn.fetch("""
            SELECT solution_id, task_id, condition, sent_at, approved_at
            FROM solution
            WHERE team_id = $1
            ORDER BY task_id
        """, team_id)

        return [{
            "solution_id": r["solution_id"],
            "task_id": r["task_id"],
            "status": r["condition"],
            "sent_at": r["sent_at"].isoformat(),
            "approved_at": r["approved_at"].isoformat() if r["approved_at"] else None
        } for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        await conn.close()

@router.get("/task_solutions")
async def get_task_solutions(
    task_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = await decode_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can view solutions")

    try:
        conn = await get_connection()
        rows = await conn.fetch("""
            SELECT solution_id, team_id, condition, answer, sent_at, approved_at
            FROM solution
            WHERE task_id = $1
            ORDER BY team_id
        """, task_id)

        return [{
            "solution_id": r["solution_id"],
            "team_id": r["team_id"],
            "status": r["condition"],
            "answer": r["answer"] if isinstance(r["answer"], dict) else json.loads(r["answer"]),
            "sent_at": r["sent_at"].isoformat(),
            "approved_at": r["approved_at"].isoformat() if r["approved_at"] else None
        } for r in rows]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        await conn.close()


@router.get("/task_solutions_short")
async def get_task_solutions_short(
    task_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = await decode_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can view solutions")

    try:
        conn = await get_connection()
        rows = await conn.fetch("""
            SELECT solution_id, team_id, condition, sent_at, approved_at
            FROM solution
            WHERE task_id = $1
            ORDER BY team_id
        """, task_id)

        return [{
            "solution_id": r["solution_id"],
            "team_id": r["team_id"],
            "status": r["condition"],
            "sent_at": r["sent_at"].isoformat(),
            "approved_at": r["approved_at"].isoformat() if r["approved_at"] else None
        } for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        await conn.close()

class TaskInput(BaseModel):
    question: str
    answer: Dict[str, Any] = Field(..., description='JSON с ключом "selections"')

@router.post("/load")
async def load_task(
    data: TaskInput,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = await decode_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can load tasks")

    if not isinstance(data.answer, dict) or "selections" not in data.answer:
        raise HTTPException(status_code=400, detail='Answer must be a JSON object with "selections"')

    try:
        conn = await get_connection()
        max_id = await conn.fetchval("SELECT MAX(task_id) FROM task") or 0
        new_id = max_id + 1

        await conn.execute("""
            INSERT INTO task (task_id, answer, qwestion, created_at)
            VALUES ($1, $2::jsonb, $3, NOW())
        """, new_id, json.dumps(data.answer), data.question)

        return {"message": "Task successfully created", "task_id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        await conn.close()


class AnswerUpdateRequest(BaseModel):
    team_id: int
    task_id: int

@router.post("/answers/approve")
async def approve_solution(
    data: AnswerUpdateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = await decode_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can approve solutions")

    try:
        conn = await get_connection()
        exists = await conn.fetchval(
            "SELECT 1 FROM solution WHERE team_id = $1 AND task_id = $2",
            data.team_id, data.task_id
        )
        if not exists:
            raise HTTPException(status_code=404, detail="Solution not found")

        await conn.execute("""
            UPDATE solution
            SET condition = 'approve', approved_at = NOW()
            WHERE team_id = $1 AND task_id = $2
        """, data.team_id, data.task_id)

        return {"message": "Solution approved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        await conn.close()


@router.post("/answers/reject")
async def reject_solution(
    data: AnswerUpdateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = await decode_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can reject solutions")

    try:
        conn = await get_connection()
        exists = await conn.fetchval(
            "SELECT 1 FROM solution WHERE team_id = $1 AND task_id = $2",
            data.team_id, data.task_id
        )
        if not exists:
            raise HTTPException(status_code=404, detail="Solution not found")

        await conn.execute("""
            UPDATE solution
            SET condition = 'reject', approved_at = NULL
            WHERE team_id = $1 AND task_id = $2
        """, data.team_id, data.task_id)

        return {"message": "Solution rejected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        await conn.close()

@router.delete("/remove")
async def remove_task(
    task_id: int = Query(..., description="ID задачи для удаления"),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = await decode_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can delete tasks")

    try:
        conn = await get_connection()
        exists = await conn.fetchval("SELECT COUNT(*) FROM task WHERE task_id = $1", task_id)
        if not exists:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

        await conn.execute("DELETE FROM solution WHERE task_id = $1", task_id)
        await conn.execute("DELETE FROM task WHERE task_id = $1", task_id)

        return {"message": f"Task with ID {task_id} successfully deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        await conn.close()

@router.delete("/answers/remove")
async def remove_solution(
    team_id: int,
    task_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = await decode_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can remove solutions")

    try:
        conn = await get_connection()
        exists = await conn.fetchval("""
            SELECT 1 FROM solution WHERE team_id = $1 AND task_id = $2
        """, team_id, task_id)
        if not exists:
            raise HTTPException(status_code=404, detail="Solution not found")

        await conn.execute("""
            DELETE FROM solution WHERE team_id = $1 AND task_id = $2
        """, team_id, task_id)

        return {"message": f"Solution for team {team_id} and task {task_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        await conn.close()

@router.delete("/clear")
async def clear_tasks(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = await decode_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can clear tasks")

    try:
        conn = await get_connection()
        await conn.execute("DELETE FROM solution")
        await conn.execute("DELETE FROM task")

        return {"message": "All tasks and solutions successfully deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        await conn.close()

@router.delete("/answers/clear")
async def clear_all_solutions(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = await decode_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can clear solutions")

    try:
        conn = await get_connection()
        await conn.execute("DELETE FROM solution")

        return {"message": "All solutions successfully deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        await conn.close()
