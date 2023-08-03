from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.database import Connect_db,SQLALCHEMY_DATABASE_URL_FOR_WORK
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas import UserDb
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter


user_router = InferringRouter()
"""
create router for the authentification
"""

# class UserDb(BaseModel):
#   id: int
#   username: str
#   email: str
#   created_at: datetime
#   avatar: str

@cbv(user_router)
class User_Avatar:
    db: Session = Depends(Connect_db(SQLALCHEMY_DATABASE_URL_FOR_WORK))
    
    @user_router.get("/users/me/", response_model=UserDb)
    async def read_users_me(self,current_user: User = Depends(auth_service.get_current_user)):
        return UserDb(id = current_user.id,
                      username = current_user.username,
                      email = current_user.email,
                      created_at=current_user.created_at,
                      avatar = current_user.avatar)


    @user_router.patch('/users/avatar', response_model=UserDb)
    async def update_avatar_user(self,file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user)):
        cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

        r = cloudinary.uploader.upload(file.file, public_id=f'NotesApp/{current_user.username}', overwrite=True)
        src_url = cloudinary.CloudinaryImage(f'NotesApp/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
        execute = repository_users.Update_Avatar(current_user.email, src_url, self.db)
        user = await execute()
        return UserDb(id = user.id,
                      username = user.username,
                      email = user.email,
                      created_at= user.created_at,
                      avatar = user.avatar)
