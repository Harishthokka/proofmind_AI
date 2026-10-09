from fastapi import APIRouter, HTTPException, Depends, Header, status
from typing import Optional, Dict, Any
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, GoogleAuthRequest, AuthResponse, UserResponse
from app.services.auth_service import auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """FastAPI dependency enforcing strict authentication."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Bearer token."
        )
    user = auth_service.get_user_from_token(authorization)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token. Please log in again."
        )
    return user

def get_optional_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """FastAPI dependency for endpoints supporting optional auth with fallback to demo user."""
    if authorization:
        user = auth_service.get_user_from_token(authorization)
        if user:
            return user
    return {
        "id": "demo-user-id",
        "email": "demo@proofmind.ai",
        "full_name": "Demo User",
        "created_at": "2026-01-01 00:00:00"
    }

@router.post("/register", response_model=AuthResponse)
def register(request: UserRegisterRequest):
    """Registers a new user account."""
    try:
        res = auth_service.register_user(request.email, request.full_name, request.password)
        return AuthResponse(
            user=UserResponse(**res["user"]),
            token=res["token"],
            message="Account registered successfully."
        )
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed.")

@router.post("/login", response_model=AuthResponse)
def login(request: UserLoginRequest):
    """Authenticates user credentials and issues a session token."""
    try:
        res = auth_service.authenticate_user(request.email, request.password)
        return AuthResponse(
            user=UserResponse(**res["user"]),
            token=res["token"],
            message="Login successful."
        )
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Authentication failed.")

@router.post("/google", response_model=AuthResponse)
def google_auth(request: GoogleAuthRequest):
    """Authenticates a user using a verified Google Identity token (ID token / credential)."""
    try:
        res = auth_service.authenticate_google_user(request.token)
        return AuthResponse(
            user=UserResponse(**res["user"]),
            token=res["token"],
            message="Google authentication successful."
        )
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Google authentication failed.")

@router.get("/me", response_model=UserResponse)
def get_me(user: Dict[str, Any] = Depends(get_current_user)):
    """Returns currently authenticated user profile."""
    return UserResponse(**user)

@router.post("/logout")
def logout(authorization: Optional[str] = Header(None)):
    """Logs out user and revokes session token."""
    if authorization:
        auth_service.logout_token(authorization)
    return {"message": "Logged out successfully."}
