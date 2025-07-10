from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from sqlalchemy.orm import Session
from crud import switchboard_crud
from schemas import switchboard_schema
from database.config import get_db

router =  APIRouter()

@router.post("/", response_model=switchboard_schema.Switchboard)
async def create_switchboard(switchboard: switchboard_schema.Switchboard, db: Session = Depends(get_db)):
    """
    Creates a new switchboard

    Args:
        switchboard (Switchboard) : The data model containing the attributes of the switchboard
        db (Session): Database session

    Returns:
        The newly created switchboard
    """
    return switchboard_crud.create_switchboard(db, switchboard=switchboard)


@router.put("/{switchboard_id}", response_model=switchboard_schema.Switchboard)
async def update_switchboard(switchboard_id: str, switchboard_update:switchboard_schema.SwitchboardUpdate, db: Session = Depends(get_db)):
    """
    Updates a switchboard

    Args:
        switchboard_id (str): The id of the switchboard we want to update
        switchboard_update (SwitchboardUpdate): The data model containing the attributes to update the switchboard
        db (Session): Database session

    Returns:
        The updated switchboard
    """
    db_switchboard = switchboard_crud.update_switchboard(db, switchboard_id=switchboard_id, switchboard_update=switchboard_update)

    if db_switchboard is None:
        raise HTTPException(status_code=500, detail="Something went wrong. Switchboard could not be updated.")

    return db_switchboard


@router.delete("/{switchboard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_switchboard(switchboard_id: str, db: Session = Depends(get_db)):
    """
    Deletes a switchboard

    Args:
        switchboard_id (str): The id of the switchboard we want to delete
        db (Session): Database session
    """
    switchboard_crud.delete_switchboard(db, switchboard_id=switchboard_id)


@router.get("/", response_model=List[switchboard_schema.Switchboard])
async def get_switchboards(skip: int = 0, limit : int = 100, db: Session = Depends(get_db)):
    """
    Returns a list of switchboards

    Args:
        skip (int, optional): The number of switchboards to skip
        limit (int, optional): The maximum number of switchboards to return
        db (Session): Database session

    Returns:
        A list of all the switchboards
    """
    return switchboard_crud.get_switchboards(db, skip=skip, limit=limit)


@router.get("/{switchboard_id}", response_model=switchboard_schema.Switchboard)
async def get_switchboard(switchboard_id: str, db: Session = Depends(get_db)):
    """
    Returns a switchboard

    Args:
        switchboard_id (str): The id of the switchboard we want to retrieve
        db (Session): Database session

    Returns:
        The switchboard
    """
    return switchboard_crud.get_switchboard(db, switchboard_id=switchboard_id)