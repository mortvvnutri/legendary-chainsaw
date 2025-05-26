from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import psycopg2
import hashlib
import jwt
import os
from datetime import datetime, timedelta, timezone
from db_connect import get_connection
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = os.getenv("JWT_SECRET", "mysecret")
ALGORITHM = "HS256"
security = HTTPBearer()

class LoginRequest(BaseModel):
    login: str
    password: str

class RegisterRequest(BaseModel):
    login: str
    password: str

def verify_password(password, hash_, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest() == hash_

TOKEN_EXP_HOURS = int(os.getenv("JWT_EXP_HOURS", 2))

def generate_token(team_id, team_name, role):
    expires = datetime.utcnow() + timedelta(hours=TOKEN_EXP_HOURS)
    payload = {
        "team_id": team_id,
        "team_name": team_name,
        "role": role,
        "exp": expires
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, expires

def decode_token(token: str):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT expires_at FROM auth_tokens WHERE token = %s", (token,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Token not found")
        expires_at = row[0]
        if datetime.now(timezone.utc) > expires_at:
            raise HTTPException(status_code=401, detail="Token expired")
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    finally:
        if 'conn' in locals():
            conn.close()

@router.post("/login", responses={
    200: {"description": "Successful login"},
    401: {"description": "Invalid credentials"},
    403: {"description": "Admin must use admin login endpoint"},
    500: {"description": "Internal server error"},
    503: {"description": "Database unavailable"}
})
def team_login(data: LoginRequest):
    if data.login.lower() == "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin must use /auth/login/admin"
        )

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT team_id, login, password_hash, password_salt FROM teams WHERE login = %s", (data.login,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=401, detail={"error": "invalid_credentials", "message": "Invalid login or password"})
        team_id, login, hash_, salt = row
        if not verify_password(data.password, hash_, salt):
            raise HTTPException(status_code=401, detail={"error": "invalid_credentials", "message": "Invalid login or password"})
        token, expires = generate_token(team_id, login, "team")
        store_token(conn, token, team_id, expires)
        return {"token": token, "team_id": team_id, "team_name": login}
    except psycopg2.OperationalError:
        raise HTTPException(status_code=503, detail="Database connection failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@router.post("/login/admin", responses={
    200: {"description": "Successful admin login"},
    401: {"description": "Invalid admin credentials"},
    500: {"description": "Internal server error"},
    503: {"description": "Database unavailable"}
})
def admin_login(data: LoginRequest):
    try:
        if data.login != "admin":
            raise HTTPException(status_code=401, detail={"error": "invalid_credentials", "message": "Invalid login or password"})
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT team_id, login, password_hash, password_salt FROM teams WHERE login = %s", ("admin",))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=401, detail={"error": "invalid_credentials", "message": "Invalid login or password"})
        team_id, login, hash_, salt = row
        if not verify_password(data.password, hash_, salt):
            raise HTTPException(status_code=401, detail={"error": "invalid_credentials", "message": "Invalid login or password"})
        token, expires = generate_token(team_id, login, "admin")
        store_token(conn, token, team_id, expires)
        return {"token": token, "team_id": team_id, "team_name": login}
    except psycopg2.OperationalError:
        raise HTTPException(status_code=503, detail="Database connection failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()
def store_token(conn, token, team_id, expires_at):
    cur = conn.cursor()
    cur.execute("SELECT MAX(token_id) FROM auth_tokens")
    max_id = cur.fetchone()[0] or 0
    new_id = max_id + 1
    cur.execute(
        "INSERT INTO auth_tokens (token_id, token, expires_at, team_id) VALUES (%s, %s, %s, %s)",
        (new_id, token, expires_at, team_id)
    )
    conn.commit()

@router.post("/register", responses={
    201: {"description": "Team successfully registered"},
    400: {"description": "Login 'admin' is reserved and cannot be used"},
    401: {"description": "Unauthorized - admin token required"},
    409: {"description": "Login already exists"},
    500: {"description": "Internal server error"},
    503: {"description": "Database unavailable"}
})
def register_team(
    data: RegisterRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can register teams")

    if data.login.lower() == "admin":
        raise HTTPException(status_code=400, detail="Login 'admin' is reserved and cannot be used")

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Check for duplicate login
        cur.execute("SELECT COUNT(*) FROM teams WHERE login = %s", (data.login,))
        if cur.fetchone()[0] > 0:
            raise HTTPException(status_code=409, detail="Login already exists")

        # Create team
        salt = os.urandom(16).hex()
        hash_ = hashlib.sha256((data.password + salt).encode()).hexdigest()
        cur.execute("SELECT MAX(team_id) FROM teams")
        max_id = cur.fetchone()[0] or 0
        new_id = max_id + 1

        cur.execute("""
            INSERT INTO teams (team_id, updated_at, login, password_hash, password_salt, created_at)
            VALUES (%s, NOW(), %s, %s, %s, NOW())
        """, (new_id, data.login, hash_, salt))

        conn.commit()
        return {"message": "Team registered successfully", "team_id": new_id, "team_name": data.login}

    except psycopg2.OperationalError:
        raise HTTPException(status_code=503, detail="Database connection failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()