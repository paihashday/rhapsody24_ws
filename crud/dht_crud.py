from fastapi import HTTPException
from typing import Optional, List
from sqlalchemy.orm import Session
from database.models import DHT_sensor, Project
from schemas import dht_schema


def create_dht_sensor(db: Session, dht: dht_schema.DHTCreate) -> DHT_sensor:
    """
    Creates a new DHT sensor in the database

    Args:
        db (Session): database session
        dht (DHTCreate): The data model containing the attributes of the sensor

    Raises:
        HTTPException: If the creation of the DHT sensor in the database fails

    Returns:
        The newly created DHT sensor
    """
    db_dht_sensor = DHT_sensor(id=dht.id, name=dht.name, ip_address=dht.ip_address, project_id=dht.project_id)
    db.add(db_dht_sensor)

    try:
        db.commit()
        db.refresh(db_dht_sensor)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create DHT sensor {str(e)}")

    return db_dht_sensor


def update_dht_sensor(db: Session, dht_id: str, dht_update: dht_schema.DHTUpdate) -> DHT_sensor:
    """
    Updates a DHT sensor

    Args:
        db (Session): database session
        dht_id (str): The id of the DHT sensor to update
        dht_update (DHTUpdate): The updated values of the DHT sensor

    Raises:
        HTTPException: If the DHT sensor does not exist
        HTTPException: If no updated values are provided
        HTTPException: If the update into the database fails

    Returns:
        The updated sensor
    """
    db_dht_sensor = db.query(DHT_sensor).filter_by(id=dht_id).first()
    if db_dht_sensor is None:
        print("Did not find DHT sensor")
        raise HTTPException(status_code=404, detail=f"DHT sensor with ID {dht_id}does not exist")

    if dht_update is not None:
        for var, value in vars(dht_update).items():
            if value is not None:
                setattr(db_dht_sensor, var, value)
    else:
        raise HTTPException(status_code=400, detail="Bad request : No data provided")


    try:
        db.commit()
        db.refresh(db_dht_sensor)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update DHT_sensor {str(e)}")

    return db_dht_sensor


def delete_dht_sensor(db: Session, dht_id: str) -> bool:
    """
    Deletes a DHT sensor

    Args:
        db (Session): A database session
        dht_id (str): The id of the DHT sensor to delete

    Returns:
        A boolean indicating if the DHT sensor was deleted
    """
    db_dht_sensor = db.query(DHT_sensor).filter_by(id=dht_id).first()
    if db_dht_sensor is not None:
        db.delete(db_dht_sensor)
        db.commit()
        return True

    return False


def get_dht_sensors(db: Session, skip: int=0, limit: int=100) -> List[DHT_sensor]:
    """
    Returns a list of DHT sensors

    Args:
        db (Session): A database session
        skip (int, optional): The number of sensors to skip at the beginning
        limit (int, optional): The maximum number of sensors to return

    Returns:
        A list of DHT sensors
    """
    return db.query(DHT_sensor).offset(skip).limit(limit).all()


def get_dht_sensor(db: Session, dht_id: str) -> Optional[DHT_sensor]:
    """
    Returns a DHT sensor

    Args:
        db (Session): A database session
        dht_id (int): The id of the DHT sensor to retrieve

    Raises:
        HTTPException: If the DHT sensor does not exist

    Returns:
        The DHT sensor
    """
    db_dht_sensor = db.query(DHT_sensor).filter_by(id=dht_id).first()

    if db_dht_sensor is None:
        raise HTTPException(status_code=404, detail="DHT sensor not found")

    return db_dht_sensor