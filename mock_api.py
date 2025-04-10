from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import time
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any

app = FastAPI(title="Mock Training API", version="1.3.0")

# Enhanced CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    user: Dict[str, Any]

class UserProfile(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None

class TrainingSession(BaseModel):
    title: str
    duration: int
    difficulty: str = "beginner"

# Database simulation
mock_db = {
    "users": {
        "test@example.com": {
            "id": "user-1",
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123",
            "role": "athlete"
        }
    },
    "training_sessions": [],
    "tokens": {}
}

# Middleware for security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# Enhanced endpoints
@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.3.0", "timestamp": time.time()}

@app.post("/auth/login")
async def login(login_data: LoginRequest):
    # Simulate authentication delay
    await asyncio.sleep(0.3)
    
    # Check credentials
    if login_data.email in mock_db["users"] and mock_db["users"][login_data.email]["password"] == login_data.password:
        user = mock_db["users"][login_data.email]
        token = f"mock-token-{int(time.time())}"
        mock_db["tokens"][token] = user["id"]
        
        return {
            "access_token": token,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }
        }
    else:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid credentials"}
        )

@app.get("/auth/me")
async def get_current_user(request: Request):
    # Get token from header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Not authenticated"}
        )
    
    token = auth_header.replace("Bearer ", "")
    if token not in mock_db["tokens"]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid token"}
        )
    
    user_id = mock_db["tokens"][token]
    for user in mock_db["users"].values():
        if user["id"] == user_id:
            return {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }

@app.get("/users/me")
async def get_user_profile(request: Request):
    # Reuse authentication logic
    user_data = await get_current_user(request)
    if isinstance(user_data, JSONResponse):
        return user_data  # Return error response
    
    return user_data

@app.put("/users/me")
async def update_user_profile(request: Request):
    # Authenticate first
    user_data = await get_current_user(request)
    if isinstance(user_data, JSONResponse):
        return user_data  # Return error response
    
    try:
        update_data = await request.json()
        user = mock_db["users"][user_data["email"]]
        
        # Update fields
        for key in update_data:
            if key != "password" and key != "id" and key in user:
                user[key] = update_data[key]
        
        await asyncio.sleep(0.3)  # Simulate DB write time
        return {"message": "Profile updated", "data": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(e)}
        )

@app.get("/training-sessions")
async def get_training_sessions(request: Request):
    # Authenticate first
    user_response = await get_current_user(request)
    if isinstance(user_response, JSONResponse):
        return user_response
    
    # Simulate processing delay
    await asyncio.sleep(0.2)
    
    return {"sessions": mock_db["training_sessions"], "total": len(mock_db["training_sessions"])}

@app.post("/training-sessions")
async def create_training_session(request: Request):
    # Authenticate first
    user_response = await get_current_user(request)
    if isinstance(user_response, JSONResponse):
        return user_response
    
    try:
        session_data = await request.json()
        new_session = {
            "id": f"session-{len(mock_db['training_sessions']) + 1}",
            **session_data,
            "created_by": user_response["id"],
            "created_at": time.time()
        }
        mock_db["training_sessions"].append(new_session)
        await asyncio.sleep(0.5)  # Simulate processing time
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=new_session
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(e)}
        )

@app.get("/training-sessions/{session_id}")
async def get_training_session(session_id: str, request: Request):
    # Authenticate first
    user_response = await get_current_user(request)
    if isinstance(user_response, JSONResponse):
        return user_response
    
    # Find the session
    for session in mock_db["training_sessions"]:
        if session["id"] == session_id:
            await asyncio.sleep(0.1)  # Simulate DB read time
            return session
    
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Training session not found"}
    )

@app.post("/email/send-test")
async def send_test_email(request: Request):
    # Authenticate first
    user_response = await get_current_user(request)
    if isinstance(user_response, JSONResponse):
        return user_response
    
    # Simulate email sending delay
    await asyncio.sleep(0.8)
    
    return {
        "status": "success", 
        "message_id": f"mock-email-{int(time.time())}"
    }

@app.post("/email/send")
async def send_email(request: Request):
    # Authenticate first
    user_response = await get_current_user(request)
    if isinstance(user_response, JSONResponse):
        return user_response
    
    try:
        email_data = await request.json()
        
        # Validate required fields
        if "to_email" not in email_data or "subject" not in email_data or "html_content" not in email_data:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Missing required fields"}
            )
        
        # Simulate email sending delay
        await asyncio.sleep(1.0)
        
        return {
            "status": "success", 
            "message_id": f"mock-email-{int(time.time())}"
        }
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(e)}
        )

# New endpoint for performance testing
@app.get("/load-test")
async def load_test_endpoint():
    await asyncio.sleep(0.1)  # Simulate 100ms processing time
    return {"message": "Load test successful"}

# Rate limiting simulation endpoint
@app.get("/test-rate-limit")
async def test_rate_limit(request: Request):
    client_ip = request.client.host
    request_count = getattr(request.app.state, f"rate_limit_{client_ip}", 0) + 1
    setattr(request.app.state, f"rate_limit_{client_ip}", request_count)
    
    # If more than 5 requests, simulate rate limiting
    if request_count > 5:
        await asyncio.sleep(0.1)
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded"},
            headers={"Retry-After": "60"}
        )
    
    await asyncio.sleep(0.05)
    return {"message": "Request successful", "count": request_count}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)