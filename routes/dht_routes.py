from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from sqlalchemy.orm import Session
from crud import dht_crud
from schemas import dht_schema
from database.config import get_db
import requests

router = APIRouter()


@router.post("/", response_model=dht_schema.DHT)
async def create_dht(dht: dht_schema.DHTCreate, db: Session = Depends(get_db)):
    """
    Creates a new DHT sensor

    Args:
        dht (DHTCreate): The data model containing the atrributes of a DHT sensor
        db (Session): Database session

    Returns:
        The newly created DHT sensor
    """
    return dht_crud.create_dht_sensor(db, dht=dht)


@router.put("/{dht_id}", response_model=dht_schema.DHT)
async def update_dht(dht_id: str, dht_update:dht_schema.DHTUpdate, db: Session = Depends(get_db)):
    """
    Updates a DHT sensor

    Args:
        dht_id (str): The id of the DHT sensor to update
        dht_update (DHTUpdate): The data model containing the atrributes of a DHT sensor
        db (Session): Database session

    Raises:
        HTTPException: If the DHT sensor does not exist

    Returns:
        The updated DHT sensor
    """
    db_dht_sensor = dht_crud.update_dht_sensor(db, dht_id=dht_id, dht_update=dht_update)

    if db_dht_sensor is None:
        raise HTTPException(status_code=404, detail="DHT sensor not found")

    return db_dht_sensor


@router.delete("/{dht_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dht_sensor(dht_id: str, db: Session = Depends(get_db)):
    """
    Deletes a DHT sensor

    Args:
        dht_id (str): The id of the DHT sensor to delete
        db (Session): Database session

    Returns:
        A confirmation message
    """
    dht_crud.delete_dht_sensor(db, dht_id=dht_id)

    return {"message": "DHT sensor deleted successfully"}


@router.get("/", response_model=List[dht_schema.DHT])
async def get_dht_sensors(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """
    Returns all DHT sensors

    Args:
        db (Session): Database session
        skip (int, optional): The offset of the first result fetch
        limit (int, optional): The maximum number of results to fetch

    Returns:
        A list of DHT sensors
    """
    return dht_crud.get_dht_sensors(db, skip=skip, limit=limit)


@router.get("/{dht_id}", response_model=dht_schema.DHT)
async def get_dht_sensor(dht_id: str, db: Session = Depends(get_db)):
    """
    Returns a DHT sensor

    Args:
        dht_id (str): The id of the DHT sensor to retrieve
        db (Session): Database session
    """
    return dht_crud.get_dht_sensor(db, dht_id=dht_id)


@router.get("/values/{dht_id}", response_model=dht_schema.DHTValues)
async def get_dht_values(dht_id: str, db: Session = Depends(get_db)):
    """
    Returns a DHT sensor values

    Args:
        dht_id (str): The id of the DHT sensor to retrieve the values from
        db (Session): Database session

    Raises:
        HTTPException: If the DHT sensor does not exist
        HTTPException: If the HTTP requests to retrieve DHT values fails

    Returns:
        The DHT sensor values and its ip_address and name
    """
    db_dht_sensor = dht_crud.get_dht_sensor(db, dht_id=dht_id)
    if db_dht_sensor is None:
        raise HTTPException(status_code=404, detail=f"DHT sensor with ID:{dht_id}, not found")

    endpoint = f"http://{db_dht_sensor.ip_address}/infos"
    try:
        response = requests.get(endpoint)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not reach sensor: {str(e)}")

    request_dht_values = response.json()
    combined_dht_values = dict()

    combined_dht_values["name"] = db_dht_sensor.name
    combined_dht_values["ip_address"] = db_dht_sensor.ip_address
    combined_dht_values["temperature_c"] = request_dht_values["temperature_c"]
    combined_dht_values["temperature_f"] = request_dht_values["temperature_f"]
    combined_dht_values["humidity"] = request_dht_values["humidity"]

    print(combined_dht_values)

    return combined_dht_values
