import logging as logger
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM
from app.db.mongoDB import AsyncIOMotorClient, get_database
from app.model.user import UserLogin, UserSignup, UserProfile, User, UserWallets
from app.service.user import userLogin, userSignup, userProfile, getUserWallet, updateUserWallet, getUserPublicProfile
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()

# instansiating OAuth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        user = User(email=email)

    except JWTError:
        raise credentials_exception

    return user


'''
@abstract: Login User
@author: DM
@version: 1.0.0
'''
@router.post("/user/login", tags=["Users"])
async def userLoginAPI(
    payload: UserLogin,
    db: AsyncIOMotorClient = Depends(get_database),
):
    logger.info("Username "+str(payload.username)+" Trying to login")
    user_login_resp = await userLogin(db, payload)

    if user_login_resp["message"] != "SUCCESS":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_login_resp["data"] }, expires_delta=access_token_expires
    )
    return {"statusCode": "200", "message": "SUCCESS", "username": payload.username, "access_token": access_token}


'''
@abstract: Sign-up User
@author: DM
@version: 1.0.0
'''
@router.post("/user/signup", tags=["Users"])
async def userSignupAPI(
    payload: UserSignup,
    db: AsyncIOMotorClient = Depends(get_database),
):
    user_signup_resp = await userSignup(db, payload)

    if user_signup_resp["message"] == "SUCCESS":
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_signup_resp["data"] }, expires_delta=access_token_expires
        )
        return {"statusCode": "200", "message": "SUCCESS", "username": payload.username, "access_token": access_token}
        
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
   


'''
@abstract: Update user profile
@author: DM
@version: 1.0.0
'''
@router.post("/user/profile", tags=["Users"])
async def updateUserProfileAPI(
    payload: UserProfile,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_database),
):
    print("current user", current_user)
    return await userProfile(db, current_user.email, payload)


'''
@abstract: Get User Public Profile
@author: DM
@version: 1.0.0
'''
@router.get("/user/profile", tags=["Users"])
async def getUserPublicProfileAPI(username: str, db: AsyncIOMotorClient = Depends(get_database)):
    logger.debug("getting user public profile")
    return await getUserPublicProfile(db, username)



'''
@abstract: update user's wallets address
@author: DM
@version: 1.0.0 
'''
@router.post("/user/wallet", tags=["Users"])
async def updateUserWalletAPI(
    payload: UserWallets,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_database),
):
    return await updateUserWallet(db, current_user.email, payload)


'''
@abstract: Get user's wallet address
@author: DM
@version: 1.0.0 
'''
@router.get("/user/wallet", tags=["Users"])
async def getUserWalletAPI(
    email: str,
    walletId: Optional[str] = None,
    db: AsyncIOMotorClient = Depends(get_database),
):
    return await getUserWallet(db, email, walletId)


