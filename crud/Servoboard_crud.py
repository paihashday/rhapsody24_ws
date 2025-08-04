from fastapi import HTTPException
from typing import Optional, List
from sqlalchemy.orm import Session
from database.models import Servoboard
from schemas import servoboard_schema


def create_servoboard(db: Session, servoboard: servoboard_schema.ServoboardSchemaCreate):
    pass


def update_servoboard():
    pass


def delete_servoboard():
    pass


def get_servoboard():
    pass


def get_servoboards():
    pass