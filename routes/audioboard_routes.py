from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from sqlalchemy.orm import Session
from crud import audioboard_crud
from schemas import audioboard_schema
from database.config import get_db

router = APIRouter()

@router.post("/", response_model=audioboard_schema.Audioboard)
async def create_audioboard(audioboard: audioboard_schema.Audioboard, db: Session = Depends(get_db)):
    """
    Creates a new audioboard

    Args:
        audioboard (Audioboard) : The data model containing the attributes of an audioboard
        db (Session) : The database session

    Returns:
        The newly created audioboard
    """
    return audioboard_crud.create_audioboard(db, audioboard=audioboard)


@router.put("/{id}", response_model=audioboard_schema.Audioboard)
async def update_audioboard(audioboard_id: str, audioboard_update:audioboard_schema.AudioboardUpdate, db: Session = Depends(get_db)):
    """
    Updates an audioboard

    Args:
        audioboard_id (str) : The id of the audioboard we want to update
        audioboard_update (AudioboardUpdate) : The data model containing the attributes of the audioboard
        db (Session) : The database session

    Returns:
        The updated audioboard
    """
    return audioboard_crud.update_audioboard(db, audioboard_id=id, audioboard_update=audioboard_update)



@router.delete("/{audioboard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_audioboard(audioboard_id: str, db: Session = Depends(get_db)):
    """
    Deletes an audioboard

    Args:
        audioboard_id (str) : The id of the audioboard we want to delete
        db (Session) : The database session
    """
    audioboard_crud.delete_audioboard(db, audioboard_id=audioboard_id)


@router.get("/", response_model=List[audioboard_schema.Audioboard])
async def get_audioboards(skip: int=0, limit: int=100, db: Session = Depends(get_db)):
    """
    Returns a list of audioboards

    Args:
        skip (int, optional) : The number of items to skip
        limit (int, optional) : The number of items to return
        db (Session) : The database session

    Returns:
        A list of audioboards
    """
    return audioboard_crud.get_audioboards(db, skip=skip, limit=limit)


@router.get("/{audioboard_id}", response_model=audioboard_schema.Audioboard)
async def get_audioboard(audioboard_id: str, db: Session = Depends(get_db)):
    """
    Returns an audioboard

    Args:
        audioboard_id (str) : The id of the audioboard we want to retrieve
        db (Session) : The database session

    Returns:
        An audioboard
    """
    return audioboard_crud.get_audioboard(db, audioboard_id=audioboard_id)


@router.get("/registered/{audioboard_id}")
async def audioboard_registered(audioboard_id:str, db:Session=Depends(get_db)):
    """
    Returns a boolean indicating if an audioboard exists

    Args:
    audioboard_id (str) : The id of the audioboard we want to check
    db (Session) : The database session
    Returns:
    A boolean indicating if an audioboard exists
    """
    exists = audioboard_crud.audioboard_registered(db, audioboard_id=audioboard_id)

    return {"exists": exists}


