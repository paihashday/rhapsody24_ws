from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from sqlalchemy.orm import Session
from crud import project_crud
from schemas import project_schema
from database.config import get_db

router = APIRouter()

@router.post("/", response_model= project_schema.Project)
async def create_project(project: project_schema.ProjectCreate, db: Session = Depends(get_db)):
    """
    Creates a new project

    Args:
        project (Project): The data model containing the attributes of the project
        db (Session): Database session

    Returns:
        The newly created project
    """
    return project_crud.create_project(db, project=project)



@router.put("/{id}", response_model=project_schema.Project)
async def update_project(id: int, project_update:project_schema.ProjectUpdate, db: Session=Depends(get_db)):
    """
    Updates a project

    Args:
        project_id (int): The id of the project we want to update
        project_update (ProjectUpdate): The data model containing the attributes of the project we want to update
        db (Session): Database session

    Returns:
        The updated project
    """
    return project_crud.update_project(db, project_id=id, project_update=project_update)



@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(id: int, db: Session = Depends(get_db)):
    """
    Deletes a project

    Args:
        project_id (int): The id of the project we want to delete
        db (Session): Database session

    Returns:
        A confirmation message
    """
    project_crud.delete_project(db, project_id=id)



@router.get("/", response_model=List[project_schema.Project])
async def get_projects(skip: int = 0, limit: int = 100, db: Session=Depends(get_db)):
    """
    Returns a list of the projects

    Args:
        skip (int, optional): The number of projects to skip at the beginning of the list
        limit (int, optional): The maximum number of projects to return
        db (Session): Database session

    Returns:
        A list of projects
    """
    return project_crud.get_projects(db, skip, limit)


@router.get("/{project_id}", response_model=project_schema.Project)
async def get_project(project_id: int, db: Session=Depends(get_db)):
    """
    Returns a project

    Args:
        project_id (int): The id of the project we want to retrieve
        db (Session): Database session

    Raises:
        HTTPException: If the project we want to retrieve does not exist

    Returns:
        The project
    """
    return project_crud.get_project_by_id(db, project_id)