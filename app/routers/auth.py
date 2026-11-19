from __future__ import annotations

import datetime
import hashlib
import uuid
from typing import Optional
from fastapi import APIRouter, Cookie, HTTPException, Request, Response, status

from app.schemas import LoginResponse, UserLogin, UserOut, UserRegister
from app.services.storage import store

router = APIRouter(prefix="/auth", tags=["Auth"])


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_current_user_from_cookie(access_token: Optional[str] = Cookie(None)) -> Optional[dict]:
    if not access_token:
        return None
    email = store.sessions.get(access_token)
    if not email:
        return None
    return store.users.get(email)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister, response: Response):
    email = payload.email.lower().strip()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email address.")
    if len(payload.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    if email in store.users:
        raise HTTPException(status_code=400, detail="Email is already registered.")

    user_id = f"usr_{uuid.uuid4().hex[:8]}"
    created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    user_record = {
        "id": user_id,
        "email": email,
        "password_hash": hash_password(payload.password),
        "full_name": payload.full_name or email.split("@")[0].capitalize(),
        "created_at": created_at,
    }
    store.users[email] = user_record

    # Create session cookie
    token = f"sess_{uuid.uuid4().hex}"
    store.sessions[token] = email
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24 * 7,
    )

    return {
        "user": {
            "id": user_record["id"],
            "email": user_record["email"],
            "full_name": user_record["full_name"],
            "name": user_record["full_name"],
            "created_at": user_record["created_at"],
        },
        "message": "User registered successfully",
    }


@router.post("/login", response_model=LoginResponse)
async def login(payload: UserLogin, response: Response):
    email = payload.email.lower().strip()
    user = store.users.get(email)
    if not user or user["password_hash"] != hash_password(payload.password):
        # Allow demo login if using demo credentials
        if email == "demo@example.com" and payload.password in ("demo123", "password", "demo"):
            user = store.users["demo@example.com"]
        else:
            raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = f"sess_{uuid.uuid4().hex}"
    store.sessions[token] = email

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24 * 7,
    )

    return LoginResponse(
        user=UserOut(
            id=user["id"],
            email=user["email"],
            full_name=user.get("full_name"),
            name=user.get("full_name"),
            created_at=user.get("created_at"),
            session_expires_at=(
                datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
            ).isoformat(),
        ),
        message="Logged in successfully",
    )


@router.post("/refresh")
async def refresh_session(
    response: Response,
    access_token: Optional[str] = Cookie(None),
):
    if not access_token or access_token not in store.sessions:
        raise HTTPException(status_code=401, detail="Session expired or invalid.")

    email = store.sessions[access_token]
    new_token = f"sess_{uuid.uuid4().hex}"
    del store.sessions[access_token]
    store.sessions[new_token] = email

    response.set_cookie(
        key="access_token",
        value=new_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24 * 7,
    )

    return {"status": "refreshed", "message": "Session renewed."}


@router.post("/logout")
async def logout(
    response: Response,
    access_token: Optional[str] = Cookie(None),
):
    if access_token and access_token in store.sessions:
        del store.sessions[access_token]

    response.delete_cookie(key="access_token")
    return {"status": "logged_out", "message": "Logged out successfully."}


@router.get("/me")
async def get_me(access_token: Optional[str] = Cookie(None)):
    user = get_current_user_from_cookie(access_token)
    if not user:
        # Default fallback to demo user if no cookie or testing directly
        user = store.users.get("demo@example.com")
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated.")

    return {
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user.get("full_name"),
            "name": user.get("full_name"),
            "created_at": user.get("created_at"),
            "session_expires_at": (
                datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
            ).isoformat(),
        }
    }
