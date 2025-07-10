from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import status
from sqlalchemy.orm import Session
from collections import defaultdict
from crud import switch_crud, switchboard_crud
from schemas import switch_schema
from database.config import get_db
import requests



router = APIRouter()


@router.post("/", response_model=switch_schema.Switch)
async def create_switch(switch: switch_schema.SwitchCreate, db: Session = Depends(get_db)):
    """
    Creates a switch

    Args:
        switch (SwitchCreate): The data model containing the attributes for the switch
        db (Session): A database session

    Returns:
        The newly created switch
    """
    return switch_crud.create_switch(db, switch=switch)


@router.put("/{switch_id}", response_model=switch_schema.Switch)
async def update_switch(switch_id: int, switch_update: switch_schema.SwitchUpdate, db: Session = Depends(get_db)):
    """
    Updates a switch

    Args:
        switch_id (int): The database ID of the switch you want to update
        switch_update (switch_update): The data model containing the updated attributes for the switch
        db: (Session): A database session

    Returns:
        db_switch: The updated switch object

    Raises:
        HTTPException: If the switch is not found (404 error)
    """
    db_switch = switch_crud.update_switch(db, switch_id=switch_id, switch_update=switch_update)
    if db_switch is None:
        raise HTTPException(status_code=404, detail="Switch not found")

    return db_switch


@router.delete("/{switch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_switch(switch_id: int, db: Session = Depends(get_db)):
    """
    Deletes a switch

    Args:
        switch_id (int): The database ID of the switch you want to delete
        db (Session): A database session
    """
    switch_crud.delete_switch(db, switch_id=switch_id)


@router.get("/{switch_id}", response_model=switch_schema.Switch)
async def get_switch(switch_id:int, db: Session = Depends(get_db)):
    """
    Retrieves a switch

    Args:
        switch_id (int): The database ID of the switch you want to retrieve
        db (Session): A database session

    Returns:
        A switch object
    """
    return switch_crud.get_switch_by_id(db, switch_id=switch_id)


@router.get("/by_name/{switch_name}", response_model=switch_schema.Switch)
def get_switch_by_name(switch_name:str, db:Session=Depends(get_db)):
    return switch_crud.get_switch_by_name(db, switch_name=switch_name)


@router.get("/list/", response_model=List[switch_schema.Switch])
async def get_switchs(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """
    Retrieves a list of switchs

    Args:
        db (Session) : A database session
        skip (int) : The offset of the first result fetch
        limit (int) : The maximum number of results to fetch

    Returns:
        A list of switch objects
    """
    return switch_crud.get_switchs(db, skip=skip, limit=limit)


@router.get("/list/{switchboard_id}", response_model=List[switch_schema.Switch])
async def get_switchs_by_switchboards(switchboard_id: str, db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """
    Retrieves a list of switchs associated with a switchboard

    Args:
        switchboard_id (str): The database ID of the switchboard associated with the switchs
        db (Session): A database session
        skip (int) : The offset of the first result fetch
        limit (int) : The maximum number of results to fetch

    Returns:
        A list of switch objects
    """
    return switch_crud.get_switchs(db, switchboard_id=switchboard_id, skip=skip, limit=limit)


@router.get("/states/{switchboard_id}")
async def get_switchs_states(switchboard_id: str, db: Session = Depends(get_db)):
    """
    Returns the state of the switches associated with a switchboard

    Args:
        switchboard_id (str): The database ID of the switchboard
        db (Session): A database session

    Raises:
        HTTPException: If no switch associated with the switchboard is found (404 error)

    Returns:
        A list of switches nicknames and their state
    """
    db_switchs = switch_crud.get_switchs(db, switchboard_id=switchboard_id)
    if db_switchs is None:
        raise HTTPException(status_code=404, detail=f"No switch associated with switchboard {switchboard_id} found")

    switchs_nicknames = ["relay1", "relay2", "relay3", "relay4", "relay5", "relay6", "relay7", "relay8"]
    switchs_states = dict()

    for switch in db_switchs:
        selected_switch_nickname = switchs_nicknames[switch.position - 1]

        if switch.state:
            str_state = "ON"
        else:
            str_state = "OFF"

        switchs_states[selected_switch_nickname] = str_state

    return switchs_states


@router.post("/lock/")
async def lock_switch(request_data: switch_schema.LockSwitchRequest, db: Session = Depends(get_db)):
    """
    Lock or unlock a list of switchs

    Args:
        switch_id (int): The database ID of the switch
        request_data (switch_schema.LockSwitchRequest): The data model containing the switch and their new lock state
        db (Session): A database session

    Returns:
        response_message: The response sent to the client

    Raises:
        HTTPException: The request data is invalid
    """
    try:
        request_data = request_data.switchs
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    errors = []
    for switch_id, lock_state in request_data.items():
        try:
            switch_crud.lock(db, switch_id, lock_state)
        except Exception as e:
            errors.append(f"Switch {switch_id} lock state was not modified : {e}")

    response_message = {"message": f"All switches have been processed with {len(errors)} errors encountered."}
    if len(errors) > 0:
        response_message["errors"] = errors

    return response_message


@router.post("/toggle/")
async def toggle_switchs(request_data: switch_schema.ToggleSwitchsRequest, db: Session = Depends(get_db)):
    """
    Receives a json body containing a list of switchs and their new state
    Sends HTTP requests to the switchboards
    Updates the states in the database

    Args:
        request_data (switch_schema.ToggleSwitchsRequest): The data model containing the switchs and their new states
        db (Session): A database session

    Returns:
        response_message : The response send to the client

    Raises:
        HTTPException: If request_data is not properly formated
    """
    switchs_nicknames = ["relay1", "relay2", "relay3", "relay4", "relay5", "relay6", "relay7", "relay8"]

    # Parses JSON from the request
    try:
        request_data = request_data.switchs
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    switchs_by_switchboard = defaultdict(lambda: defaultdict(str)) # The dict in which the switchs will be sorted by switchboards
    errors = [] # The list of errors

    for switch_id, state in request_data.items():
        # Retrieves the switch in the database
        db_switch = switch_crud.get_switch(db, switch_id=switch_id)
        if db_switch is None:
            errors.append(f"Switch with ID {switch_id} not found")
            continue

        if db_switch.locked is True:
            errors.append(f"Switch {switch_id} state is locked and cannot be updated")
            continue

        # Retrieves the switchboard associated with the switch in the database
        db_switchboard = switchboard_crud.get_switchboard(db, switchboard_id=db_switch.switchboard_id)
        if db_switchboard is None:
            errors.append(f"Could not find switchboard associated with switch (ID : {switch_id}")
            continue

        # Gives a nickname to the switch accordingly to what it requested by the API
        # of the switchboard.
        selected_switch_nickname = switchs_nicknames[db_switch.position - 1]

        # Converts switch_state from boolean to a string
        if state:
            str_state = "ON"
        else:
            str_state = "OFF"

        # Add the switch and its state
        switchs_by_switchboard[db_switchboard.id][selected_switch_nickname] = str_state

    for switchboard_id, switchs in switchs_by_switchboard.items():

        # Prepares the HTTP request
        payload = {}
        for switch, state in switchs.items():
            payload[switch] = state

        # Retrieves the switchboard associated with the switchs
        db_switchboard = switchboard_crud.get_switchboard(db, switchboard_id=switchboard_id)

        endpoint = f"http://{db_switchboard.ip_address}/control"
        headers = {"Content-Type": "application/json"}

        # Sends the request
        try:
            response = requests.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
            print(f"Request send to {db_switchboard.ip_address}")
        except requests.RequestException as e:
            errors.append(f"Request error for {db_switchboard.ip_address} : {str(e)}")
            continue

        # Updates the database
        for switch, state in switchs.items():
            db_switch = switch_crud.get_switch(db, switchboard_id=db_switchboard.id, position=switchs_nicknames.index(switch) + 1)
            if db_switch is None:
                errors.append(f"Switch with nickname {switch} on switchboard {db_switchboard.id} not found")
                continue

            if state == "OFF":
                switch_crud.toggle(db, switch_id=db_switch.id, state=False)
            elif state == "ON":
                switch_crud.toggle(db, switch_id=db_switch.id, state=True)
            else:
                errors.append(f"Invalid state for switch {switch}")
                continue

    response_message = {"message": f"All switches have been processed with {len(errors)} errors encountered."}
    if errors:
        response_message["errors"] = errors

    return response_message