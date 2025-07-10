from fastapi import HTTPException
from typing import Optional, List
from sqlalchemy.orm import Session
from database.models import Switchboard
from schemas import switchboard_schema


def create_switchboard(db: Session, switchboard: switchboard_schema.SwitchboardCreate) -> Switchboard:
    """
    Creates a new switchboard in the database

    Args:
        db (Session): A database session
        switchboard (SwitchboardCreate): The data model expected to create a switchboard

    Raises:
        HTTPException: The switchboard cannot be created in the database

    Returns:
        The newly created switchboard
    """
    db_switchboard = Switchboard(id=switchboard.id, name=switchboard.name, ip_address=switchboard.ip_address, project_id=switchboard.project_id)
    db.add(db_switchboard)

    try:
        db.commit()
        db.refresh(db_switchboard)
    except:
        db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong")

    return db_switchboard


def update_switchboard(db: Session, switchboard_id: str, switchboard_update: switchboard_schema.SwitchboardUpdate) -> Optional[Switchboard]:
    """
    Updates a switchboard in the database

    Args:
        db (Session): A database session
        switchboard_id (str): The id of the switchboard
        switchboard_update (SwitchboardUpdate): The data model used to update the switchboard

    Raises:
        HTTPException: The switchboard cannot be found in the database
        HTTPException: The expected values are not properly provided
        HTTPException: The switchboard cannot be updated in the database

    Returns:
        The updated switchboard
    """
    db_switchboard = db.query(Switchboard).filter_by(id=switchboard_id).first()
    if db_switchboard is None:
        raise HTTPException(status_code=404, detail="Switchboard not found")

    if switchboard_update is not None:
        for var, value in vars(switchboard_update).items():
            if value is not None:
                setattr(db_switchboard, var, value)
    else:
        raise HTTPException(status_code=400, detail="Bad request. No data provided")

    try:
        db.commit()
        db.refresh(db_switchboard)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Something went wrong: {e}")

    return db_switchboard


def delete_switchboard(db: Session, switchboard_id: str) -> bool:
    """
    Deletes a switchboard in the database

    Args:
        db (Session): A database session
        switchboard_id (str): The id of the switchboard to delete

    Returns:
        A boolean indicating if the switchboard was deleted
    """
    db_switchboard = db.query(Switchboard).filter_by(id=switchboard_id).first()
    if db_switchboard is not None:
        db.delete(db_switchboard)
        db.commit()
        return True

    return False


def get_switchboards(db: Session, skip: int=0, limit: int=100) -> List[Switchboard]:
    """
    Returns a list of all the switchboards from the database

    Args:
        db (Session): A database session
        skip (int, optional): The number of switchboards to skip at the begining of the list.
        limit (int, optional): The maximum number of switchboards to return.

    Returns:
        A list of all the switchboards
    """
    return db.query(Switchboard).offset(skip).limit(limit).all()


def get_switchboard(db: Session, switchboard_id: str) -> Optional[Switchboard]:
    """
    Returns a switchboard from the database

    Args:
        db (Session): A database session
        switchboard_id: The id of the switchboard to retrieve

    Raises:
        HTTPException: The switchboard cannot be found in the database

    Returns:
        The switchboard
    """
    db_switchboard = db.query(Switchboard).filter_by(id=switchboard_id).first()

    if db_switchboard is None:
        raise HTTPException(status_code=404, detail="Switchboard not found")

    return db_switchboard


