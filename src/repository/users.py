from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel
from abc import abstractmethod
"""
contains a common part for all derived classes
"""


class BaseUser:

  def __init__(self, db: Session):
    self.db = db

  @abstractmethod
  async def __call__(self):
    pass


class Get_User_by_Email(BaseUser):

  def __init__(self, email: str, db: Session):
    super().__init__(db)
    self.email = email

  async def __call__(self) -> User:
    return self.db.query(User).filter(User.email == self.email).first()

class Confirm_Email(BaseUser):
  def __init__(self,email:str, db:Session):
    super().__init__(db)
    self.email = email

  async def __call__(self)->None:
    execute = Get_User_by_Email(self.email, self.db)
    user = await execute()
    user.confirmed = True
    self.db.commit()

class Create_User(BaseUser):

  def __init__(self, body: UserModel, db: Session):
    super().__init__(db)
    self.body = body

  async def __call__(self) -> User:
    avatar = None
    try:
      g = Gravatar(self.body.email)
      avatar = g.get_image()
    except Exception as e:
      print(e)
    new_user = User(**self.body.dict(), avatar=avatar)
    self.db.add(new_user)
    self.db.commit()
    self.db.refresh(new_user)
    return new_user


class Update_Token(BaseUser):

  def __init__(self, user: User, token: str, db: Session):
    super().__init__(db)
    self.user = user
    self.token = token

  async def __call__(self) -> None:
    self.user.refresh_token = self.token
    self.db.commit()

class Update_Avatar(BaseUser):
  def __init__(self, email:str, src_url:str, db:Session):
    super().__init__(db)
    self.email = email
    self.url = src_url

  async def __call__(self) -> User:
      execute = Get_User_by_Email(self.email,self.db)
      user = await execute()
      user.avatar = self.url
      self.db.commit()
      return user  
