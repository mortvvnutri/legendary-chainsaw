from fastapi import APIRouter, HTTPException
from db_connect import get_connection
import asyncpg

router = APIRouter(prefix="/ping", tags=["ping"])

@router.get("/", responses={
    200: {"description": "Server is running"},
    500: {"description": "Internal server error"}
})
async def ping():
    try:
        return {"status": "Server is running"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/bd_connect", responses={
    200: {"description": "Database connection successful"},
    503: {"description": "Database unavailable"},
    500: {"description": "Unexpected server error"}
})
async def ping_db():
    try:
        conn = await get_connection()
        await conn.close()
        return {"status": "Database connection successful"}
    except asyncpg.PostgresError as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")