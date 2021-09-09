from typing import Dict,  Optional
from pydantic import validator
from app.model.rwmodel import RWModel


class User(RWModel):
    email: str
    username: Optional[str] = None

class UserSignup(RWModel):
    username: str
    email: str
    password: str
    is_emailVerify: Optional[bool] = False
    status: Optional[str] # User account status (Active, Inactive, Deactivate)
    member_since : Optional[str] 

class UserLogin(RWModel):
    username: str
    password: str

class UserProfile(RWModel):
    full_name:str
    username: str
    profession_type: str
    about_me: Optional[str]
    support_type: str # support type like pizza, coffee, samosa, crypto
    online_presence: Optional[Dict[str, str]] # user's websie and socail media if any
    avatar: Optional[str] # user profile picture

class UserWallets(RWModel):
    wallet: Optional[Dict[str, Dict[str, str]]]


class PublicUserProfile(RWModel):
    full_name:str = None
    username: str = None
    profession_type: str = None
    about_me: str = None
    support_type: str = None# support type like pizza, coffee, samosa, crypto
    online_presence: Dict[str, str]  = None# user's websie and socail media if any
    avatar: str = None # user profile picture
    wallet: Dict[str, Dict[str, str]] = None
