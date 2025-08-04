from fastapi import HTTPException
from typing import Optional, List
from sqlalchemy.orm import Session
from database.models import Switch
from schemas import switch_schema


def create_switch(db: Session, switch: switch_schema.SwitchCreate) -> Switch:
    """
    Creates a new switch in the database

    Args:
        db (Session): Database session
        switch (SwitchCreate): The data model of a project

    Raises:
        HTTPException: 500 - The switch cannot be added to the database

    Returns:
        The newly created switch
    """
    db_switch = Switch(name=switch.name, position=switch.position, state=switch.state, switchboard_id=switch.switchboard_id)
    db.add(db_switch)

    try:
        db.commit()
        db.refresh(db_switch)
    except:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create a switch")

    return db_switch


def update_switch(db: Session, switch_id: int, switch_update: switch_schema.SwitchUpdate) -> Switch:
    """
    Updates a switch in the database

    Args:
        db (Session): Database session
        switch_id (int): The id of the switch
        switch_update (SwitchUpdate): The data model used to update the switch

    Raises:
        HTTPException: 404 - The switch cannot be found
        HTTPException: 400 - The data provided to update the switch is not conform to the SwitchUpdate data model
        HTTPException: 500 - The switch cannot be updated in the database

    Returns:
        The updated switch
    """
    db_switch = db.query(Switch).filter_by(id=switch_id).first()
    if db_switch is None:
        raise HTTPException(status_code=404, detail="Switch not found")

    # Filter to remove empty fields
    update_data = switch_update.dict(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="Bad request. You must provide valid data to update the switch")

    # Apply updates
    for var, value in update_data.items():
        setattr(db_switch, var, value)

    # Save data in the database
    try:
        db.commit()
        db.refresh(db_switch)
    except:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update switch")

    return db_switch


def delete_switch(db: Session, switch_id: int) -> bool:
    """
    Deletes a switch from the database

    Args:
        db (Session): Database session
        switch_id (int): The id of the switch

    Returns:
        A boolean indicating if the switch was deleted
    """

    db_switch = db.query(Switch).filter_by(id=switch_id).first()
    if db_switch is not None:
        db.delete(db_switch)
        db.commit()
        return True

    return False


def get_switchs(db: Session, skip: int=0, limit: int=100) -> List[Switch]:
    """
    Returns a list of switches

    Args:
        db (Session): Database session
        skip (int, optional): The number of switches to skip at the beginning of the list
        limit (int, optional): The maximum number of switches to return

    Returns:
        A list of switches
    """
    return db.query(Switch).offset(skip).limit(limit).all()



def get_switchboard_switchs(db:Session, switchboard_id:str, skip:int=0, limit:int=100) -> List[Switch]:
    """
    Returns a list of swithces associated with switchboard which id is provided

    Args:
        db (Session): Database session
        switchboard_id (str): The id of the switchboard
        limit (int, optional): The maximum number of switches to return
        skip (int, optional): The number of switches to skip at the beginning of the list

    Returns:
        A list of switches
    """
    if switchboard_id is not None:
        return db.query(Switch).filter_by(switchboard_id=switchboard_id).offset(skip).limit(limit).all()
    else:
        HTTPException(status_code=400, detail="Bad request. You must provide a switchboard_id.")


def get_switch(db:Session, switch_id:int=None, switchboard_id:str=None, position:int=None):
    if switch_id is not None:
        return db.query(Switch).filter_by(id=switch_id).first()
    elif switchboard_id is not None and position is not None:
        return db.query(Switch).filter_by(switchboard_id=switchboard_id, position=position).first()
    else:
        raise HTTPException(status_code=400, detail="Bad request. You must provide a switch_id or a switchboard_id and a switch_position.")



def get_switch_by_id(db: Session, switch_id:int) -> Optional[Switch]:
    """
    Returns a switch

    Args:
        db (Session): Database session
        switch_id (int, optional): The id of the switch to retrieve
        position (int, optional): The position of the switch on the switchboard

    Raises:
        HTTPException: 404 - The switch cannot be found

    """
    return db.query(Switch).filter_by(id=switch_id).first()



def get_switch_by_name(db:Session, switch_name:str, switchboard_id:str) -> Optional[Switch]:
    """
    Returns a switch by its name

    Args:
        db (Session): Database session
        switch_name (str): The name of the switch
        switchboard_id (str): The id of the switchboard associated with the switch

    Raises:
        HTTPException: 404 - The switch cannot be found

    Returns:
        A switch
    """
    if switch_name is None or switchboard_id is None:
        raise HTTPException(status_code=400, detail="Bad request. You must provide a switch_name and a switchboard_id.")
    else:
        db_switch = db.query(Switch).filter_by(switchboard_id=switchboard_id).filter_by(name=switch_name).first()
        if db_switch is None:
            raise HTTPException(status_code=404, detail="Switch not found")
        return db_switch



def toggle(db: Session, switch_id: int, state: bool) -> Switch:
    """
    Changes the switch state

    Args:
        db (Session): Database session
        switch_id (int): The id of the switch
        state (bool): The new state of the switch

    Raises:
        HTTPException: 404 - The switch cannot be found
        HTTPException: 403 - The switch state is locked and cannot be updated
        HTTPException: 500 - The switch cannot be updated in the database

    Returns:
        The updated switch
    """
    db_switch = db.query(Switch).filter_by(id=switch_id).first()
    if db_switch is None:
        raise HTTPException(status_code=404, detail=f"Switch with ID {switch_id} not found.")

    if db_switch.locked is False:
        db_switch.state = state
    else:
        raise HTTPException(status_code=403, detail=f"Switch state is locked and cannot be updated.")

    try:
        db.commit()
        db.refresh(db_switch)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Something went wrong : {e}")

    return db_switch


def lock(db: Session, switch_id: int, lock: bool) -> Switch:
    """
    Change the lock state of a switch
    The lock state indicates if the switch state (on/off) can be modified

    Args:
        db (Session): Database session
        switch_id (int): The id of the switch
        lock (bool, optional): Whether the switch state is locked

    Raises:
        HTTPException: 404 - The switch cannot be found
        HTTPException: 500 - The switch lock state cannot be updated in the database

    Returns:
        The updated switch
    """
    db_switch = db.query(Switch).filter_by(id=switch_id).first()
    if db_switch is None:
        raise HTTPException(status_code=404, detail=f"Switch with ID {switch_id} cannot be found")

    db_switch.locked = lock

    try:
        db.commit()
        db.refresh(db_switch)
    except:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save 'lock' state in the database for switch with ID {db_switch.id}")

    return db_switch