from fastapi import HTTPException, APIRouter, status, Depends
from typing import Annotated

import models
from database import get_db

from schemas import UserUpdate, UserCreate, UserPrivate, Token

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy import func
from authen import currentUser, create_access_token, hash_pw, verify_pw
from config import settings


router = APIRouter()

@router.post("/register", response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db:Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(func.lower(models.User.username) == user.username.lower()))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists."
        )
    
    result = await db.execute(select(models.User).where(func.lower(models.User.email) == user.email.lower()))

    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Email already exists."
        )
    
    new_user = models.User(
        username = user.username,
        email = user.email.lower(),
        password_hash = hash_pw(user.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


#login func
@router.post("/login", response_model=Token)
async def login_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[AsyncSession, Depends(get_db)]):
    res = await db.execute(select(models.User).where(func.lower(models.User.email) == form_data.username.lower()))

    user = res.scalars().first()  
    if not user or not verify_pw(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )  
    
    acess_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=acess_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")
 

#to get the current user
@router.get("/me", response_model=UserPrivate)
async def get_curent_user(current_user: currentUser):
   return current_user


@router.delete("/delete/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_acc(user_id: int, current_user:currentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = "Not authorized."
        )

    result = await db.execute(select(models.User).where(models.User.id == user_id).options(selectinload(models.User.posts)))
    currUser = result.scalars().first()
    if not currUser:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "User not found")
    
    await db.delete(currUser)
    await db.commit()

    return None


@router.put("/search/{user_id}", response_model=UserPrivate)
async def update_account(user_id: int, currentUser: currentUser, user_update:UserUpdate ,db:Annotated[AsyncSession, Depends(get_db)]):
    if user_id != currentUser.id:
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user."
        )
    
    res = await db.execute(select(models.User).where(models.User.id == user_id))
    result = res.scalars().first()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    if user_update.username is not None and user_update.username.lower()  != result.username.lower():
        res = await db.execute(select(models.User).where(func.lower(models.User.username) == user_update.username.lower()))
        existing_user = res.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code= status.HTTP_400_BAD_REQUEST,
                detail="Username already exists."
            )
        
    if(user_update.email is not None and user_update.email.lower() != result.email.lower()):
        result = await db.execute(select(models.User).where(func.lower(models.User.email) == user_update.email.lower()))
        existing_email = result.scalars().first()
        if existing_email:
            raise HTTPException(
                status_code= status.HTTP_400_BAD_REQUEST,
                detail="Email already exists."
            )

    if user_update.username is not None:
        result.username = user_update.username
    if user_update.email is not None:
        result.email = user_update.email.lower()
    if user_update.image_file is not None:
        result.image_file = user_update.image_file

    await db.commit()
    await db.refresh(result)
    return result