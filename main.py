from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# --- Database Setup ---
DATABASE_URL = "sqlite:///./availability.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Database Model ---
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)
    initials = Column(String(10), nullable=False)
    is_available = Column(Boolean, default=True)

Base.metadata.create_all(bind=engine)

# --- Pydantic Schemas ---
class UserResponse(BaseModel):
    id: int
    name: str
    role: str
    initials: str
    is_available: bool

    model_config = ConfigDict(from_attributes=True)

class AvailabilityUpdateRequest(BaseModel):
    is_available: bool

# --- App Setup & Data Seeding ---
app = FastAPI(title="Team Availability Tracker")

def seed_database():
    """Seed initial 9 team members matching the mockup data."""
    db = SessionLocal()
    try:
        if db.query(UserDB).count() == 0:
            initial_users = [
                UserDB(id=1, name="Aisha Khan", role="Frontend Engineer", initials="AK", is_available=True),
                UserDB(id=2, name="Daniel Okafor", role="QA Engineer", initials="DO", is_available=False),
                UserDB(id=3, name="Priya Nair", role="Data Analyst", initials="PN", is_available=True),
                UserDB(id=4, name="Marcus Lee", role="Backend Engineer", initials="ML", is_available=False),
                UserDB(id=5, name="Mei Tanaka", role="Product Manager", initials="MT", is_available=True),
                UserDB(id=6, name="Sofia Rossi", role="Product Designer", initials="SR", is_available=True),
                UserDB(id=7, name="Lucas Silva", role="DevOps Engineer", initials="LS", is_available=True),
                UserDB(id=8, name="Tom Becker", role="Support Lead", initials="TB", is_available=False),
                UserDB(id=9, name="Elena Petrova", role="Engineering Manager", initials="EP", is_available=True),
            ]
            db.add_all(initial_users)
            db.commit()
    finally:
        db.close()

seed_database()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints ---

# Fetch all users
@app.get("/api/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(UserDB).order_by(UserDB.id.asc()).all()

# Update availability toggle
@app.patch("/api/users/{user_id}/availability", response_model=UserResponse)
def update_availability(user_id: int, request: AvailabilityUpdateRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_available = request.is_available
    db.commit()
    db.refresh(user)
    return user

# Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)