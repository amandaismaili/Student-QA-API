from fastapi import HTTPException, APIRouter, Depends, status
from typing import Annotated

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from schemas import ReplyResponse, Reply, PostCreate, PostResponse, PostUpdate
from database import get_db

from authen import currentUser

router = APIRouter()

@router.get("", response_model=list[PostResponse])
async def get_section(db: Annotated[AsyncSession, Depends(get_db)]):
    res =  await db.execute(select(models.Questions).options(selectinload(models.Questions.author)))
    data = res.scalars().all()
    return data

@router.post("/questions", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def make_question(ques: PostCreate, currentUser: currentUser,db:Annotated[AsyncSession, Depends(get_db)]):
    question = models.Questions(
        user_id= currentUser.id,
        title= ques.title,
        content = ques.content
    )

    db.add(question)
    await db.commit()
    await db.refresh(question, attribute_names=["author"])
    return question


@router.post("/reply", response_model=ReplyResponse, status_code=status.HTTP_201_CREATED)
async def post_reply(reply_body: Reply, currentUser: currentUser, db:Annotated[AsyncSession, Depends(get_db)]):
    reply = models.Replies(
        question_id = reply_body.question_id,
        user_id = currentUser.id,
        content = reply_body.reply
    )

    db.add(reply)
    await db.commit()
    await db.refresh(reply)

    return reply


@router.get("/search/{question_id}", response_model=PostResponse)
async def search(question_id: int, db:Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Questions).where(models.Questions.id == question_id).options(selectinload(models.Questions.author)))
    res = result.scalars().first()

    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found.")
    
    return res
 

@router.delete("/question/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(question_id: int, current_user: currentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    res = await db.execute(select(models.Questions).where(models.Questions.id == question_id).options(selectinload(models.Questions.author)))
    result = res.scalars().first()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found.")
    
    if result.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update this post.")
    
    await db.delete(result)
    await db.commit()

    return None


@router.delete("/reply/{reply_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reply(reply_id: int, current_user: currentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    res = await db.execute(select(models.Replies).where(models.Replies.id == reply_id))
    result = res.scalars().first()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reply not found.")
    
    if result.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update this post.")
    
    await db.delete(result)
    await db.commit()

    return None


@router.put("/search/{question_id}", response_model=PostResponse)
async def update_full_post(question_id: int, currentUser: currentUser, post_data: PostCreate, db:Annotated[AsyncSession, Depends(get_db)]):
    res = await db.execute(select(models.Questions).where(models.Questions.id == question_id))
    result = res.scalars().first()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found.")
    
    if result.user_id != currentUser.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update this post.")

    result.title = post_data.title
    result.content = post_data.content 

    await db.commit()
    await db.refresh(result, attribute_names=["author"])
    return result


@router.patch("/search/{question_id}", response_model=PostResponse)
async def update_post(question_id: int, post_data: PostUpdate, current_user: currentUser, db:Annotated[AsyncSession, Depends(get_db)]):
    res = await db.execute(select(models.Questions).where(models.Questions.id == question_id).options(selectinload(models.Questions.author)))
    result = res.scalars().first()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found.")
    
    if result.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update this post.")

    update_data = post_data.model_dump(exclude_unset = True)
    for field, val in update_data.items():
        setattr(result, field, val)
    
    await db.commit()
    await db.refresh(result, attribute_names=["author"])
    return result
