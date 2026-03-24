from fastapi import APIRouter, HTTPException, Response, Request, status, Depends
from app.schema.userLogIn import UserLogIn
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.userDataDBModel import UserDataDBModel
from app.utils.hashpassword import verify_password
from app.utils.jwt import create_access_token, get_current_user

router = APIRouter(prefix="/auth")

@router.post("/login")
def login(login_data: UserLogIn, response: Response, db: Session = Depends(get_db)):
    # check in db
    user = db.query(UserDataDBModel).filter(UserDataDBModel.userEmail_id== login_data.userEmail_id).first()
    if not user or not verify_password(login_data.userPassword,user.userPassword):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    
    # Create JWT token
    token = create_access_token({
        "user_id": user.id,
        "role": user.userRole
    })

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # Set to False for localhost HTTP
        samesite="lax",
        path="/"  # Make cookie available for all paths
    )
    return {
        "message": "Login successfully"
    }

@router.get("/me")
def get_me(request: Request, db: Session = Depends(get_db)):
    """Verifies session and returns current user info."""
    try:
        user = get_current_user(request, db)
        return {"id": user.id, "role": user.userRole, "email": user.userEmail_id}
    except Exception:
        raise HTTPException(status_code=401, detail="Not logged in")

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message":"Logout successfully"}