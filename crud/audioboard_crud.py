from fastapi import HTTPException
from typing import Optional, List
from sqlalchemy.orm import Session
from database.models import Audioboard
from schemas import audioboard_schema


def create_audioboard(db: Session, audioboard: audioboard_schema.AudioboardCreate) -> Audioboard:
    """
    Creates a new audioboard in the database

    Args:
        db (Session): The database session
        audioboard (AudioboardCreate) : The data model containing the attributes of an audioboard

    Raises:
        HTTPException: The audioboard cannot be created in the database

    Returns:
        The newly created audioboard
    """
    db_audioboard = Audioboard(id=audioboard.id, name=audioboard.name, ip_address=audioboard.ip_address, api_port=audioboard.api_port, project_id=audioboard.project_id)
    db.add(db_audioboard)

    try:
        db.commit()
        db.refresh(db_audioboard)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Something went wrong while attempting to create an audioboard : {e}')

    return db_audioboard


def update_audioboard(db: Session, audioboard_id: str, audioboard_update: audioboard_schema.AudioboardUpdate) -> Optional[Audioboard]:
    """
    Updates an audioboard in the database

    Args:
        db (Session): The database session
        audioboard_id (str): The id of the audioboard
        audioboard_update (audioboard_schema.AudioboardUpdate): The data model containing the attributes of an audioboard

    Raises:
        HTTPException: The audioboard cannot be found in the database
        HTTPException: The expected values are not properly provided
        HTTPException: The audioboard cannot be updated in the database

    Returns:
        The updated audioboard
    """
    db_audioboard = db.query(Audioboard).filter_by(id=audioboard_id).first()
    if db_audioboard is None:
        raise HTTPException(status_code=404, detail=f"Audioboard with ID: {audioboard_id} was not found")

    if audioboard_update is not None:
        for var, value in vars(audioboard_update).items():
            if value is not None:
                setattr(db_audioboard, var, value)
    else:
        raise HTTPException(status_code=400, detail=f"Bad request. Incomplete or incorrect audioboard data provided.")

    try:
        db.commit()
        db.refresh(db_audioboard)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Something when wrong while updating the audioboard: {e}")

    return db_audioboard


def delete_audioboard(db: Session, audioboard_id: str) -> bool:
    """
    Deletes an audioboard from the database

    Args:
        db (Session): The database session
        audioboard_id (str): The id of the audioboard

    Returns:
        A boolean indicating if the audioboard was deleted
    """
    db_audioboard = db.query(Audioboard).filter_by(id=audioboard_id).first()
    if db_audioboard is not None:
        try:
            db.delete(db_audioboard)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Something when wrong while deleting an audioboard : {e}")

        return True
    else:
        return False


def audioboard_registered(db:Session, audioboard_id:str) -> bool:
    """
    Returns True if an audioboard exists in the database

    Args:
    db (Session): The database session
    audioboard_id (str): The id of the audioboard
    Returns:
    A boolean indicating if the audioboard exists in the database
    """
    return db.query(Audioboard).filter_by(id=audioboard_id).count() > 0



def get_audioboards(db: Session, skip: int=0, limit: int=100) -> List[Audioboard]:
    """
    Returns a list of audioboards from the database

    Args:
        db (Session): The database session
        skip (int, optional): The number of audioboards to skip at the beginning of the list.
        limit (int, optional): The maximum number of audioboards to return.

    Returns:
        A list of audioboards
    """
    return db.query(Audioboard).offset(skip).limit(limit).all()


def get_audioboard(db: Session, audioboard_id: str) -> Optional[Audioboard]:
    """
    Returns an audioboard from the database

    Args:
        db (Session): The database session
        audioboard_id (str): The id of the audioboard

    Raises:
        HTTPException: The audioboard cannot be found in the database

    Returns:
        The audioboard
    """
    db_audioboard = db.query(Audioboard).filter_by(id=audioboard_id).first()

    if db_audioboard is None:
        raise HTTPException(status_code=404, detail=f"Audioboard not found")

    return db_audioboard

