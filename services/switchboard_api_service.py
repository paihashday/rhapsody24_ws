import httpx
import asyncio
from typing import Dict, Any, List, Tuple
from crud import switch_crud, switchboard_crud
from sqlalchemy.orm import Session
from schemas import switch_schema
from fastapi import HTTPException
from collections import defaultdict

switchs_nicknames = ["relay1", "relay2", "relay3", "relay4", "relay5", "relay6", "relay7", "relay8"]


def build_switchs_by_switchboard(db: Session, request_data: switch_schema.ToggleSwitchsRequest) -> Tuple[Dict[str, Dict[str, str]], List[str]]:
    """
    Creates and organize the payloads by switchboards

    Args:
        db (Session): database session
        request_data (switch_schema.ToggleSwitchsRequest): The data model expected to toggle switchs

    Returns:
    Tuple[Dict[str, Dict[str, str]], List[str]]: A tuple containing the organized payloads and a list of error messages
    """
    request_data = request_data.switchs

    switchs_by_switchboard = defaultdict(lambda: defaultdict(str)) # The dict in which the switchs will be sorted by switchboards
    errors = [] # The list of errors

    for switch_id, state in request_data.items():
        # Retrieves the switch in the database
        db_switch = switch_crud.get_switch(db, switch_id=switch_id)
        if db_switch is None:
            errors.append(f"Switch with id {switch_id} not found.")
            continue

        if db_switch.locked is True:
            errors.append(f"Switch with id {switch_id} is locked and cannot be toggled.")

        # Retrieves the switchboard associated with the switch in the database
        db_switchboard = switchboard_crud.get_switchboard(db, switchboard_id=db_switch.switchboard_id)
        if db_switchboard is None:
            errors.append(f"Switchboard with id {db_switch.switchboard_id} not found.")
            continue

        # Gives a nickname to the switch accordingly to what is required by the API
        # of the switchboard
        selected_switch_nickname = switchs_nicknames[db_switch.position - 1]

        # Convert the switch state from boolean to string
        if state:
            str_state = "ON"
        else:
            str_state = "OFF"

        # Add the switch and its state
        switchs_by_switchboard[db_switchboard.id][selected_switch_nickname] = str_state


    return (switchs_by_switchboard, errors)



async def send_switchboard_request(db: Session, switchboard_id: str, switchs: Dict[str, str]) -> Dict[str, Any]:
    """
    Sends a HTTP request to the switchboard

    Args:
    db (Session): database session
    switchboard_id(str): id of the switchboard
    switchs (Dict[str, str]): A dictionary with the relays and their states

    Returns:
    Dict[str, Any]: The result of the HTTP request
    """

    db_switchboard = switchboard_crud.get_switchboard(db, switchboard_id=switchboard_id)
    if db_switchboard is None:
        return {
            "switchboard_id": switchboard_id,
            "status": "failed",
            "error" : f"Switchboard with id {switchboard_id} not found in the database.",
        }

    payload = switchs
    #for switch, state in switchs.items():
    #    payload[switch] = state

    endpoint = f"http://{db_switchboard.ip_address}/control"
    headers = {"Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            return {
                "switchboard_id": switchboard_id,
                "status": "success",
                "response_status_code": response.status_code,
                "payload_sent": payload
            }
    except Exception as e:
        return {
            "switchboard_id": switchboard_id,
            "status": "failed",
            "error": str(e),
            "payload_sent": payload
        }



async def send_multiple_switchboard_requests(db: Session, switchs_by_switchboard: Dict[str, Dict[str, str]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Uses send_switchboard_request to send multiple switchboards requests in a row

    Args:
    db (Session): database session
    switchs_by_switchboard (Dict[str, Dict[str, str]]): A dictionary with the relays and their states grouped by switchboards

    Returns:
    Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]: Dictionnaries containing the success and the errors messages.
    """

    tasks = []
    success = []
    errors = []

    for switchboard_id, switchs in switchs_by_switchboard.items():
        task = send_switchboard_request(db, switchboard_id, switchs)
        tasks.append(task)

    results = await asyncio.gather(*tasks)

    for res in results:
        if res["status"] == "success":
            success.append(res)
        else:
            errors.append(res)

    return success, errors


def update_database(db: Session, switchs_by_switchboard: Dict[str, Dict[str, str]], success: List[Dict[str, Any]]) -> List[str]:
    """
    Updates the switches in the database

    Args:
    db (Session): database session
    switchs_by_switchboard (Dict[str, Dict[str, str]]): A dictionary with the relays and their states grouped by switchboards
    success (List[Dict[str, Any]]): List of the successful switchboard requests

    Returns:
    List[str]: List of updates errors
    """

    errors = []

    for result in success:
        switchboard_id = result["switchboard_id"]
        switchs = switchs_by_switchboard.get(switchboard_id)
        for switch, state in switchs.items():
            db_switch = switch_crud.get_switch(db, switchboard_id=switchboard_id, position=switchs_nicknames.index(switch) + 1)
            if db_switch is None:
                errors.append(f"Switch associated with nickname {switch} associated with switchboard {switchboard_id} not found in the database.")
                continue

            if state == "ON":
                switch_crud.toggle(db, switch_id=db_switch.id, state=True)
            elif state == "OFF":
                switch_crud.toggle(db, switch_id=db_switch.id, state=False)
            else:
                errors.append(f"Invalid state for switch {switchs_nicknames[switch]} : {state}.")


    return errors


async def process_toggle_request(db: Session, request_data: switch_schema.ToggleSwitchsRequest):
    """
    Wrapper function that processes async switchs toggles

    Args:
        db (Session): database session
        request_data (switch_schema.ToggleSwitchsRequest): The data model expected, containing all the switches to toggle
        and their states

    Returns:
        Dict[str, Any]: A list of error messages
    """

    errors = []

    switchs_by_switchboard, building_errors = build_switchs_by_switchboard(db, request_data)
    requests_success, request_errors = await  send_multiple_switchboard_requests(db, switchs_by_switchboard)
    update_database(db, switchs_by_switchboard, requests_success)

    for build_error in building_errors:
        errors.append(build_error)

    for request_error in request_errors:
        errors.append(request_error)

    return errors

