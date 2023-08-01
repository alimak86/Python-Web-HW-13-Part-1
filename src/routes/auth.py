from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.database import Connect_db, SQLALCHEMY_DATABASE_URL_FOR_WORK
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail
from src.repository import users as repository_users
from src.services.auth import auth_service

from fastapi_utils.cbv import cbv
from fastapi_utils.guid_type import GUID
from fastapi_utils.inferring_router import InferringRouter


from src.services.email import email_service

#authentification_router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()
authentification_router = InferringRouter()
"""
create router for the authentification
"""

@cbv(authentification_router)
class Login:
  db: Session = Depends(Connect_db(SQLALCHEMY_DATABASE_URL_FOR_WORK))

  @authentification_router.post("/auth/signup",
                                response_model=UserResponse,
                                status_code=status.HTTP_201_CREATED)
  async def signup(self, body: UserModel, background_tasks: BackgroundTasks, request: Request):
    execute = repository_users.Get_User_by_Email(body.email, self.db)
    exist_user = await execute()
    if exist_user:
      raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                          detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    execute = repository_users.Create_User(body, self.db)
    new_user = await execute()
    background_tasks.add_task(email_service.send_email, new_user.email, new_user.username, request.base_url)
    return UserResponse(user=new_user, detail="User successfully created. Check your email for confirmation.")
#    return {"user": new_user, "detail": "User successfully created"}

  @authentification_router.post("/auth/login", response_model=TokenModel)
  async def login(self, body: OAuth2PasswordRequestForm = Depends()):
    execute = repository_users.Get_User_by_Email(body.username, self.db)
    user = await execute()
    if user is None:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                          detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
        
    if not auth_service.verify_password(body.password, user.password):
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                          detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(
      data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(
      data={"sub": user.email})
    execute = repository_users.Update_Token(user, refresh_token, self.db)
    await execute()
    return TokenModel(access_token=access_token,
                      refresh_token=refresh_token,
                      token_type="bearer")


###    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

  @authentification_router.get('/auth/refresh_token', response_model=TokenModel)
  async def refresh_token(
    self, credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    execute = repository_users.Get_User_by_Email(email,self.db)
    user = await execute()
    if user.refresh_token != token:
      await repository_users.update_token(user, None, self.db)
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                          detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(
      data={"sub": email})
    execute = repository_users.Update_Token(user, refresh_token, self.db)
    await execute()
    return TokenModel(access_token=access_token,
                      refresh_token=refresh_token,
                      token_type="bearer")
    ###return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

  @authentification_router.get('/confirmed_email/{token}')
  async def confirmed_email(self,token: str):
    email = await auth_service.get_email_from_token(token)
    execute = repository_users.Get_User_by_Email(email,self.db)
    user = await execute()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    execute = repository_users.Confirm_Email(email,self.db)
    await execute()
    return {"message": "Email confirmed"}

  @authentification_router.post('/request_email')
  async def request_email(self,body: RequestEmail, background_tasks: BackgroundTasks, request: Request):
    user = await repository_users.get_user_by_email(body.email, self.db)
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(email_service.send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}  