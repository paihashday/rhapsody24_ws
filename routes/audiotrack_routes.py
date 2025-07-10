from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from sqlalchemy.orm import Session
from crud import audiotrack_crud, audioboard_crud
from schemas import audiotrack_schema
from database.config import get_db
import requests

router = APIRouter()

@router.post('/')
async def create_audiotrack(audiotrack:audiotrack_schema.AudiotrackCreate, db:Session=Depends(get_db)):
    """
    Creates a new audiotrack on the rhapsody_player API. If the creation succeed, adds the audiotrack to
    the database and returns it

    Args:
        audiotrack (audiotrack_schema.AudiotrackCreate): The data model containing the values of the audiotrack to be created
        db (Session): A database session

    Returns:
        The newly created audiotrack
    """
    audioboard = audioboard_crud.get_audioboard(db=db, audioboard_id=audiotrack.audioboard_id)
    if audioboard is None:
        raise HTTPException(status_code=404, detail=f"Could not find an audioboard with ID: {audiotrack.audioboard_id}")
    else:
        payload = {
            "name": audiotrack.name,
            "audio_path": audiotrack.audio_path,
            "loop": audiotrack.loop,
            "random": audiotrack.random,
            "track_id": audiotrack.track_id
        }

        endpoint = f"http://{audioboard.ip_address}:8080/audiotracks"
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            return {"error": str(err)}

        audiotrack_db = audiotrack_crud.create_audiotrack(db=db, audiotrack=audiotrack)

        return audiotrack_db



@router.put('/{track_id}', response_model=audiotrack_schema.Audiotrack)
async def update_audiotrack(track_id:int, audiotrack_update:audiotrack_schema.AudiotrackUpdate, db:Session=Depends(get_db)):
    """
    Updates an audiotrack on the player server and in the database

    Args:
    track_id (int): The id of the audiotrack to be updated
    audiotrack_update (audiotrack_schema.AudiotrackUpdate): The data model containing the values of the audiotrack to be updated
    db (Session): A database session

    Returns:
    The updated audiotrack
    """

    # Check data integrity
    if audiotrack_update is None:
        raise HTTPException(status_Code=400, detail=f"Missing or invalid update data.")

    audiotrack_db = audiotrack_crud.get_audiotrack(db=db, track_id=track_id)
    if audiotrack_crud is None:
        raise HTTPException(status_code=404, detail=f"Track with ID {track_id} not found.")

    audioboard_db = audioboard_crud.get_audioboard(db=db, audioboard_id=audiotrack_db.audioboard_id)
    if audioboard_db is None:
        raise HTTPException(status_code=404, detail=f"Audioboard associated with track (ID: {track_id} not registered.")


    # Updates track on the player server
    payload = {
        "name": audiotrack_update.name,
        "audio_path": audiotrack_update.audio_path,
        "loop": audiotrack_update.loop,
        "random": audiotrack_update.random
    }

    url = f"http://{audioboard_db.ip_address}:8080/audiotracks/settings/{track_id}"
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
    except requests.RequestException as err:
        print("Could not update audiotrack settings. They will be saved in the database and sent again at the next player server reboot.")
    finally:
        # Saves changes in the database
        return audiotrack_crud.update_audiotrack(db=db, track_id=track_id, audiotrack_update=audiotrack_update)


@router.post('/control/{track_id}')
async def control(track_id:int, action:str, db:Session=Depends(get_db)):
    authorized_actions = {"play", "pause", "resume", "stop"}

    if action not in authorized_actions:
        raise HTTPException(status_code=404, detail=f"Action {action} is not authorized.")

    audiotrack_db = audiotrack_crud.get_audiotrack(db=db, track_id=track_id)
    if audiotrack_db is None:
        raise HTTPException(status_code=404, detail=f"Track with ID {track_id} not found.")

    audioboard_db = audioboard_crud.get_audioboard(db=db, audioboard_id=audiotrack_db.audioboard_id)
    if audioboard_db is None:
        raise HTTPException(status_code=404, detail=f"Audioboard associated with track (ID: {track_id}) is not registered.")

    url = f"http://{audioboard_db.ip_address}:8080/audiotracks/control/{track_id}?action={action}"

    try:
        response = requests.post(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Could not send control request : {str(e)}")


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_audiotrack(id:int, db:Session=Depends(get_db)):
    """
    Deletes an existing audiotrack

    Args:
        id (int): The id of the audiotrack to delete
        db (Session): A database session
    """
    # TODO : Delete the audiotrack on rhapsody_player then delete it in the database
    audiotrack_crud.delete_audiotrack(db, id)


@router.get('/{id}', response_model=audiotrack_schema.Audiotrack)
async def get_audiotrack(id:int, db:Session=Depends(get_db)):
    """
    Returns an audiotrack

    Args:
        id (int): The id of the audiotrack to get
        db (Session): A database session

    Returns:
        The audiotrack
    """
    return audiotrack_crud.get_audiotrack(db, id)


@router.get('/list/', response_model=List[audiotrack_schema.Audiotrack])
async def get_audiotracks(audioboard_id:str=None, skip:int=0, limit:int=100, db:Session=Depends(get_db)):
    """
    Returns a list of audiotracks

    Args:
        audioboard_id (str): The id of an audioboard. If given, the function will return a list of audiotracks associated
        with that audioboard.
        skip (int): The number of audiotracks to skip at the beginning of the list
        limit (int): The maximum number of audiotracks to return
        db (Session): A database session

    Returns:
        A list of audiotracks
    """
    return audiotrack_crud.get_audiotracks(db, skip=skip, limit=limit, audioboard_id=audioboard_id)

