from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi.openapi.models import APIKey
import psycopg2
from db_connect import get_connection

router = APIRouter(prefix="/ping", tags=["ping"])

@router.get("/", responses={
    200: {"description": "Server is running"},
    500: {"description": "Internal server error"}
})
def ping():
    try:
        return {"status": "Server is running"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/bd_connect", responses={
    200: {"description": "Database connection successful"},
    503: {"description": "Database unavailable"},
    500: {"description": "Unexpected server error"}
})
def ping_db():
    try:
        conn = get_connection()
        conn.close()
        return {"status": "Database connection successful"}
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")