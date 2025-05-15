from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, User, Cost
from app.schemas import UserCreate, Token, CostCreate, CostResponse
from app.auth import (
    create_jwt_token,
    verify_password,
    hash_password,
    oauth2_scheme,
    decode_jwt_token,
)
from app.utils import log_audit

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    user_id = decode_jwt_token(token)
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/register/", response_model=Token)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    hashed_password = hash_password(user.password)
    db_user = User(username=user.username, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    token = create_jwt_token({"user_id": db_user.id})
    log_audit("user.register", {"user_id": db_user.id, "username": db_user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/login/", response_model=Token)
def login(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_jwt_token({"user_id": db_user.id})
    log_audit("user.login", {"user_id": db_user.id})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/costs/", response_model=CostResponse)
def add_cost(
    cost: CostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_cost = Cost(
        name=cost.name,
        amount=cost.amount,
        merchant_name=cost.merchant_name,
        description=cost.description,
        user_id=current_user.id,
    )
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)

    log_audit(
        "cost.created",
        {
            "user_id": current_user.id,
            "cost_id": db_cost.id,
            "name": db_cost.name,
            "amount": db_cost.amount,
        },
    )
    return db_cost

@app.get("/costs/", response_model=list[CostResponse])
def get_costs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Cost)
        .filter(Cost.user_id == current_user.id)
        .all()
    )
