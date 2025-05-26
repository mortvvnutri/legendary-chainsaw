from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import hashlib
import jwt
import os
from datetime import datetime, timedelta
from db_connect import get_connection
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = os.getenv("JWT_SECRET", "mysecret")
ALGORITHM = "HS256"
security = HTTPBearer()
TOKEN_EXP_HOURS = int(os.getenv("JWT_EXP_HOURS", 2))


class LoginRequest(BaseModel):
    login: str
    password: str


class RegisterRequest(BaseModel):
    login: str
    password: str


def verify_password(password, hash_, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest() == hash_


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


async def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        team_id = payload.get("team_id")

        if not team_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        conn = await get_connection()
        try:
            row = await conn.fetchrow("SELECT 1 FROM teams WHERE team_id = $1", team_id)
            if not row:
                raise HTTPException(status_code=401, detail="Team does not exist")
        finally:
            await conn.close()

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/login")
async def team_login(data: LoginRequest):
    if data.login.lower() == "admin":
        raise HTTPException(status_code=403, detail="Admin must use /auth/login/admin")

    try:
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                "SELECT team_id, login, password_hash, password_salt FROM teams WHERE login = $1",
                data.login
            )
            if not row:
                raise HTTPException(status_code=401, detail={"error": "invalid_credentials", "message": "Invalid login or password"})

            if not verify_password(data.password, row["password_hash"], row["password_salt"]):
                raise HTTPException(status_code=401, detail={"error": "invalid_credentials", "message": "Invalid login or password"})

            token, _ = generate_token(row["team_id"], row["login"], "team")
            return {"token": token, "team_id": row["team_id"], "team_name": row["login"]}
        finally:
            await conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/login/admin")
async def admin_login(data: LoginRequest):
    if data.login != "admin":
        raise HTTPException(status_code=401, detail={"error": "invalid_credentials", "message": "Invalid login or password"})

    try:
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                "SELECT team_id, login, password_hash, password_salt FROM teams WHERE login = $1",
                "admin"
            )
            if not row or not verify_password(data.password, row["password_hash"], row["password_salt"]):
                raise HTTPException(status_code=401, detail={"error": "invalid_credentials", "message": "Invalid login or password"})

            token, _ = generate_token(row["team_id"], row["login"], "admin")
            return {"token": token, "team_id": row["team_id"], "team_name": row["login"]}
        finally:
            await conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/register")
async def register_team(
    data: RegisterRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    payload = await decode_token(credentials.credentials)

    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Only admin can register teams")

    if data.login.lower() == "admin":
        raise HTTPException(status_code=400, detail="Login 'admin' is reserved and cannot be used")

    try:
        conn = await get_connection()
        try:
            exists = await conn.fetchval("SELECT COUNT(*) FROM teams WHERE login = $1", data.login)
            if exists:
                raise HTTPException(status_code=409, detail="Login already exists")

            salt = os.urandom(16).hex()
            hash_ = hashlib.sha256((data.password + salt).encode()).hexdigest()
            max_id = await conn.fetchval("SELECT MAX(team_id) FROM teams") or 0
            new_id = max_id + 1

            await conn.execute("""
                INSERT INTO teams (team_id, updated_at, login, password_hash, password_salt, created_at)
                VALUES ($1, NOW(), $2, $3, $4, NOW())
            """, new_id, data.login, hash_, salt)

            return {"message": "Team registered successfully", "team_id": new_id, "team_name": data.login}
        finally:
            await conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
