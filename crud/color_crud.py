from fastapi import HTTPException
from typing import Optional, List
from sqlalchemy.orm import Session
from database.models import Color as Color
from schemas import color_schema


def create_color(db: Session, color: color_schema.ColorCreate) -> Color:
    """
    Creates a new color

    Args:
        db (Session): the database session
        color (color_schema.ColorCreate): the data model of a color

    Raises:
        HTTPException: 500 - The color cannot be added to the database

    Returns:
        The newly created color
    """
    db_color = Color(name=color.name, red_value=color.red_value, green_value=color.green_value, blue_value=color.blue_value, white_value=color.white_value)
    db.add(db_color)

    try:
        db.commit()
        db.refresh(db_color)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create a color: {e}")

    return db_color


def update_color(db: Session, color_id: int, color: color_schema.ColorUpdate) -> Color:
    """
    Updates a color

    Args:
    db (Session) : the database session
    color (color_schema.ColorUpdate): The data model expected to update a color

    Raises:
    HTTPException: 404 - The color cannot be found
    HTTPException: 400 - The data provided to update the color is not conform to the ColorUpdate data model
    HTTPException: 500 - The color cannot be updated in the database

    Returns:
        The updated color
    """
    db_color = db.query(Color).filter_by(id=color_id).first()
    if db_color is None:
        raise HTTPException(status_code=404, detail=f"Color with id {color_id} not found")

    if color is None:
        raise HTTPException(status_code=400, detail=f"Color with id {color_id} could not be updated because the updated values are not conform to the color_schema.")

    try:
        for var, value in vars(color).items():
            if value is not None:
                setattr(db_color, var, value)
        db.commit()
        db.refresh(db_color)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update color with id : {color_id} : {e}")

    return db_color


def get_colors(db: Session, skip:int=0, limit:int=100) -> List[Color]:
    """
    Retrieves a list of all the colors

    Args:
        db (Session): the database session
        skip (int): the number of colors to skip
        limit (int): the number of colors to return

    Returns:
        A list of all the colors
    """
    return db.query(Color).offset(skip).limit(limit).all()


def get_color(db: Session, color_id: int) -> Color:
    """
    Retrieves a color by id

    Args:
        db (Session): the database session
        color_id (int): the id of the color

    Raises:
        HTTPException: 404 - The color cannot be found

    Returns:
        The color by id
    """
    db_color = db.query(Color).filter_by(id=color_id).first()

    if db_color is None:
        HTTPException(status_code=404, detail=f"Color with id {color_id} not found.")

    return db_color
