from jose import jwt, JWTError
from datetime import datetime,timedelta
from fastapi import Request,HTTPException,status
from sqlalchemy.orm import Session
from app.models.userDataDBModel import UserDataDBModel

SECRET_KEY = 'SECRET123'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data:dict):
    to_encode = data.copy()
    expire = datetime.utcnow()+ timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp':expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm= ALGORITHM)

def get_current_user(request:Request, db:Session):
    token = request.cookies.get('access_token')
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = db.query(UserDataDBModel).filter(UserDataDBModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
    