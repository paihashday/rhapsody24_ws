from fastapi import HTTPException
from typing import Optional, List
from sqlalchemy.orm import Session
from database.models import Audiotrack
from schemas import audiotrack_schema


def create_audiotrack(db:Session, audiotrack:audiotrack_schema.AudiotrackCreate) -> Audiotrack:
    """
    Creates a new audiotrack in the database

    Args:
    db (Session): A database session
    audiotrack (audiotrack_schema.AudiotrackCreate): The expected data model of an audiotrack

    Returns:
        The newly created audiotrack.
    """
    db_audiotrack = Audiotrack(name=audiotrack.name, audio_path=audiotrack.audio_path, loop=audiotrack.loop, random=audiotrack.random, audioboard_id=audiotrack.audioboard_id)
    db.add(db_audiotrack)

    try:
        db.commit()
        db.refresh(db_audiotrack)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Something went wrong {str(e)}")

    return db_audiotrack



def update_audiotrack(db:Session, track_id:int, audiotrack_update:audiotrack_schema.AudiotrackUpdate) -> Audiotrack:
    """
    Updates an existing audiotrack in the database

    Args:
        db (Session): A database session
        track_id (int): The id of the audiotrack to update
        audiotrack_update (audiotrack_schema.AudiotrackUpdate): The expected data model of an audiotrack

    Returns:
        The updated audiotrack.
    """
    db_audiotrack = db.query(Audiotrack).filter_by(track_id=track_id).first()
    if db_audiotrack is None:
        raise HTTPException(status_code=404, detail=f"Audiotrack with ID {track_id} not found.")

    if audiotrack_update is None:
        raise HTTPException(status_code=400, detail=f"Bad request. Incomplete or incorrect audiotrack data")

    for var, value in vars(audiotrack_update).items():
        if value is not None:
            setattr(db_audiotrack, var, value)

    try:
        db.commit()
        db.refresh(db_audiotrack)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Something went wrong : {str(e)}")

    return db_audiotrack



def delete_audiotrack(db:Session, track_id:int) -> bool:
    db_audiotrack = db.query(Audiotrack).filter_by(track_id=track_id).first()
    if db_audiotrack is None:
        raise HTTPException(status_code=404, detail=f"Audiotrack with ID {track_id} not found.")

    try:
        db.delete(db_audiotrack)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Something went wrong {str(e)}")

    return True


def get_audiotrack(db:Session, track_id:int) -> Optional[Audiotrack]:
    db_audiotrack = db.query(Audiotrack).filter_by(track_id=track_id).first()
    if db_audiotrack is None:
        raise HTTPException(status_code=404, detail=f"Audiotrack with ID {track_id} not found.")

    return db_audiotrack


def get_audiotracks(db:Session, skip:int, limit:int,  audioboard_id:str=None) -> List[Audiotrack]:
    try:
        if audioboard_id is None:
            return db.query(Audiotrack).offset(skip).limit(limit).all()
        else:
            return db.query(Audiotrack).filter_by(audioboard_id=audioboard_id).offset(skip).limit(limit).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong {str(e)}")