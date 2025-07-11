from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from sqlalchemy.orm import Session
from crud import color_crud
from schemas import color_schema
from database.config import get_db

router = APIRouter()


@router.post("/", response_model=color_schema.Color)
async def create_color(color: color_schema.ColorCreate, db: Session = Depends(get_db)):
    """
    Creates a new color

    Args:
        color (color_schema.ColorCreate): The data model expected to create a color
        db (Session): Database session

    Returns:
        The newly created color
    """
    return color_crud.create_color(db, color)


@router.put("/{id}", response_model=color_schema.Color)
async def update_color(id: int, color: color_schema.ColorUpdate, db: Session = Depends(get_db)):
    """
    Updates a given color

    Args:
        id (int): The id of the color
        color (color_schema.ColorUpdate): The data model expected to update the color
        db (Session): Database session

    Returns:
        The updated color
    """
    return color_crud.update_color(db, id, color)


@router.get('/list', response_model=List[color_schema.Color])
async def get_colors(skip:int=0, limit:int=100, db:Session=Depends(get_db)):
    """
    Retrieves all the colors

    Args:
        skip (int): The number of colors to skip
        limit (int): The number of colors to return
        db (Session): Database session

    Returns:
        A list of colors
    """
    return color_crud.get_colors(db, skip, limit)


@router.get('/{id}', response_model=color_schema.Color)
async def get_color(id:int, db:Session=Depends(get_db)):
    """
    Retrieves a color by its id

    Args:
        id (int): The id of the color
        db (Session): Database session

    Returns:
        The color
    """
    return color_crud.get_color(db, id)