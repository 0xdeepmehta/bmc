import math
import time
import base64
import secrets
import hashlib
import logging as logger
from app.core.config import RANDOM_STRING_CHARS, DATABASE_NAME, USER_COLLECTIONS
from app.model.user import UserLogin, UserSignup, UserProfile, UserWallets, PublicUserProfile
from app.db.mongoDB import AsyncIOMotorClient

'''
@abstract: generate securely random string
@author: @DM
@version: 1.0.0
'''
async def get_random_string(length: int, allowed_chars: str= RANDOM_STRING_CHARS) -> str:
    """
    Return a securely generated random string.
    """
    return ''.join(secrets.choice(allowed_chars) for _ in range(length))


'''
@abstract: Generate securely random salt
@author: @DM
@version: 1.0.0
'''
async def generate_salt():
    """
    Generate a cryptographically secure nonce salt in ASCII with an entropy
    of at least `salt_entropy` bits.
    """
    salt_entropy = 128
    char_count = math.ceil(salt_entropy / math.log2(len(RANDOM_STRING_CHARS)))
    return await get_random_string(char_count, allowed_chars=RANDOM_STRING_CHARS)


'''
@abstract: Method to hash password
@author:  @DM
@version 1.0.0
'''
async def hash_password(password: str):
    """Turn a plain-text password into a hash using salt and sha256 for database storage

    Parameters
    ==========
    password(str): user given password

    Returns
    =======
    str: hashed version of user password
    """
    iterations = 320000
    digest = hashlib.sha256()

    logger.debug("Hashing user password ...")
    salt = await generate_salt()
    pwdhash = hashlib.pbkdf2_hmac(
        digest.name,
        password.encode('utf-8'),
        salt.encode('utf-8'),
        iterations
    )
    pwdhash =  base64.b64encode(pwdhash).decode('ascii').strip()

    return "%s$%s" % (salt, pwdhash)


'''
@abstract Verifty stored password for login
@author: @DM
@version 1.0.0
'''
async def verify_password(stored_password, provided_password):
    logger.debug("Verifying user password ..")
    """Verify a stored password against one provided by user"""

    digest = hashlib.sha256()
    iterations = 320000
    salt, hash = stored_password.split('$')

    pwdhash = hashlib.pbkdf2_hmac(digest.name,
                                  provided_password.encode('utf-8'),
                                  salt.encode('utf-8'),
                                  iterations)
    pwdhash =  base64.b64encode(pwdhash).decode('ascii').strip()
    if hash == pwdhash:
        print("Password verified")
        return True
    else:
        print("Wrong password")
        return False

'''
@abstract Check username exist or not
@author JM
@version 1.0.0
'''
async def checkUserName(conn: AsyncIOMotorClient, username: str):
    response = {}
    logger.debug("Checking user name availiblity ...")
    try:
        count = await conn[DATABASE_NAME][USER_COLLECTIONS].count_documents({'username':username})
        if(count > 0):
            logger.debug("Username already exist")
            response['status'] = "200"
            response['message'] = "USERNAME_EXIST"
        else:
            logger.debug("Username not exist")
            response['status'] = "200"
            response['message'] = "USERNAME_NOT_EXIT"

    except Exception as e:
        logger.debug("Exception occured while checking username")
        logger.error(e)
        response['status'] = 500
        response['message'] = "ERROR_OCCURED"

    return response

'''
@abstract Check email exist or not
@author JM
@version 1.0.0
'''
async def checkUserEmail(conn: AsyncIOMotorClient, email: str):
    response = {}
    logger.debug("Checking user email ...")
    try:
        count = await conn[DATABASE_NAME][USER_COLLECTIONS].count_documents({'email':email})
        if(count > 0):
            logger.debug("Email exist")
            response['status'] = "200"
            response['message'] = "EMAIL_EXIST"
        else:
            logger.debug("Email Not exist")
            response['status'] = "200"
            response['message'] = "EMAIL_NOT_EXIT"

    except Exception as e:
        logger.debug("Exception occured while checking User Email")
        logger.error(e)
        response['status'] = "500"
        response['message'] = "ERROR_OCCURED"

    return response

'''
@abstract Validating username
@author DM
@version 1.0.0
'''
async def validateUsername(username:str):

    response = {}
    logger.debug("validating username ...")
    try:
        if(username.isalnum() and len(username) <=10):
            logger.debug("Valid username")
            response['status'] = "200"
            response['message'] = "VALID_USERNAME"
        else:
            logger.debug("Invalid username")
            response['status'] = "500"
            response['message'] = "INVALID_USERNAME"

    except Exception as e:
        logger.debug("Exception occured while Validating username")
        logger.error(e)
        response['status'] = "500"
        response['message'] = "ERROR_OCCURED"

    return response


'''
@abstract: Checking user credentials
@author: @DM
@version: 1.0.0
'''
async def userLogin(conn: AsyncIOMotorClient, payload: UserLogin):
    '''
    return user profile if credentials is correct else raise exception along with correct HttpCode and message
    '''
    response = {}

    logger.debug("Authenticating user ...")

    # checking if user exist and active
    row = await conn[DATABASE_NAME][USER_COLLECTIONS].find_one({"username": payload.username, "status": "ACTIVE"})

    if row is not None:
        if await verify_password(row["password"], payload.password):
            logger.debug("Authentication successfully")

            response['statusCode'] = "200"
            response['message'] = "SUCCESS"
            response['data'] = row["email"]
        
        else:
            # incase of wrong password
            response['statusCode'] = "200"
            response['message'] = "WRONG_PASSWORD"
    else:
        logger.debug("User not found")
        response['statusCode'] = "200"
        response['message'] = "USER_NOT_EXIST"

    return response


'''
@abstract: Register new user
@author: @DM
@version: 1.0.0
'''
async def userSignup(conn: AsyncIOMotorClient, payload: UserSignup):

    response = {}
    logger.debug("Creating user account ...")
    try:

        email_cnt = await checkUserEmail(conn, payload.email)
        if(email_cnt['status'] == "200" and email_cnt['message'] == "EMAIL_EXIST"):
            response['statusCode'] = "500"
            response['message'] = "EMAIL_ALREADY_EXISTED"
            return response

        # hashing user password
        h_password = await hash_password(payload.password)
        # generate a url_safe token for email verification
        email_verify_token = secrets.token_urlsafe()

        localtime = time.localtime()
        update_datetime = time.strftime("%Y-%m-%d %H:%M:%S %z", localtime)
        payload.password = h_password
        payload.status = "ACTIVE"
        payload.member_since = update_datetime

        # convert payload to dict type
        payload = dict(payload)

        # saving some email validation
        payload["email_verify_token"] = email_verify_token
        payload["is_email_verify"] = False

        logger.debug("Saving user account ...")
        await conn[DATABASE_NAME][USER_COLLECTIONS].insert_one(payload)
        logger.debug("User account created successfully")
        response['statusCode'] = "200"
        response['message'] = "SUCCESS"
        response['data'] = {'email': payload['email']}
    except Exception as e:
        logger.debug("Error occured while creating user account")
        logger.error(e)
        response['statusCode'] = "500"
        response['message'] = "US001"

    return response



'''
@abstract: Update user profile
@author: DM
@version: 1.0.0
'''
async def userProfile(conn: AsyncIOMotorClient, current_user, payload: UserProfile):

    response = {}

    logger.debug("Updating user profile ...")

    # checking if user exist and active
    row = await conn[DATABASE_NAME][USER_COLLECTIONS].find_one({"email": current_user, "status": "ACTIVE"})

    if row is not None:
        await conn[DATABASE_NAME][USER_COLLECTIONS].update_one(
            {"email": current_user, "status": "ACTIVE"}, 
            {
                '$set': {
                    "full_name": payload.full_name,
                    "username": payload.username, 
                    "profession_type": payload.profession_type,
                    "about_me": payload.about_me,
                    "support_type": payload.support_type,
                    "online_presence": payload.online_presence,
                    "avatar": payload.avatar
                }
            }
        )

        # returing updated profile
        logger.debug("User details updated successfully")
        response['statusCode'] = "200"
        response['message'] = "SUCCESS"

    else:
        logger.debug("User not found")
        response['statusCode'] = "200"
        response['message'] = "USER_NOT_EXIST"

    return response


'''
@abstract: Get user's public profile
@author: DM
@version: 1.0.0
'''
async def getUserPublicProfile(conn: AsyncIOMotorClient, username) -> PublicUserProfile:
    response = {}
    logger.debug("Updating user profile ...")
    row = await conn[DATABASE_NAME][USER_COLLECTIONS].find_one({"username": username, "status": "ACTIVE"})

    # returing updated profile
    logger.debug("User details updated successfully")
    response['statusCode'] = "200"
    response['message'] = "SUCCESS"
    response['data'] = PublicUserProfile(**row)
    return response


'''
@abstract: Update user wallet
@author: DM
@version: 1.0.0
'''
async def updateUserWallet(conn: AsyncIOMotorClient, current_user, payload: UserWallets):
    response = {}
    logger.debug("Updating user wallet ...")

    # checking if user exist and active
    row = await conn[DATABASE_NAME][USER_COLLECTIONS].find_one({"email": current_user, "status": "ACTIVE"})
    print(row)


    if row is not None:
        print("updating ....")
        await conn[DATABASE_NAME][USER_COLLECTIONS].update_one(
            {"email": current_user, "status": "ACTIVE"}, 
            {
                '$set': {
                    "wallet": payload.wallet
                }
            }
        )
        logger.debug("User details updated successfully")
        response['statusCode'] = "200"
        response['message'] = "SUCCESS"

    else:
        logger.debug("User not found")
        response['statusCode'] = "200"
        response['message'] = "USER_NOT_EXIST"

    return response


'''
@abstract: get specific or all  user wallet
@author: DM
@version: 1.0.0
'''
async def getUserWallet(conn: AsyncIOMotorClient, email:str, walletId:str = None):
    response = {}
    logger.debug("Getting user wallet ...")

    # if walletId is none then return all user wallet's address
    userWallets = await conn[DATABASE_NAME][USER_COLLECTIONS].find_one({"email": email, "status": "ACTIVE"})
    print(userWallets)

    if walletId == None:
        logger.debug("gettting all user's address")
        response['statusCode'] = "200"
        response['message'] = "SUCCESS"
        response['data'] = userWallets['wallet']

    else:
        if userWallets["wallet"].get(walletId):
            logger.debug("gettting single users's address")
            response['statusCode'] = "200"
            response['message'] = "SUCCESS"
            response['data'] = userWallets["wallet"].get(walletId)
        else:
            response['statusCode'] = "200"
            response['message'] = "INVALID_WALLET"

    return response


        

        