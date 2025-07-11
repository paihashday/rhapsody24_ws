from fastapi import HTTPException
from typing import Optional, List
from sqlalchemy.orm import Session
from database.models import Project
from schemas import project_schema


def create_project(db: Session, project: project_schema.ProjectCreate) -> Project:
    """
    Creates a new project

    Args:
        db (Session): A database session
        project (ProjectCreate): The data model of a project

    Raises:
        HTTPException: An error occurs while creating a project

    Returns:
        The newly created project
    """
    db_project = Project(name=project.name, description=project.description, activated=project.activated)
    db.add(db_project)

    try:
        db.commit()
        db.refresh(db_project)
    except:
        db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong")
    return db_project


def update_project(db: Session, project_id: int, project_update: project_schema.ProjectUpdate) -> Optional[Project]:
    """
    Updates a project

    Args:
        db (Session): A database session
        project_id (int): The id of the project to update
        project_update (ProjectUpdate): The data model used to update the project

    Raise:
        HTTPException: The project cannot be found
        HTTPException: The data model used to update the project is not valid

    Returns:
        The updated project
    """
    db_project = db.query(Project).filter_by(id=project_id).first()

    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    if project_update is None:
        raise HTTPException(status_code=400, detail="Bad request. You must provide valid update data")

    try:
        for var, value in vars(project_update).items():
            if value is not None:
                setattr(db_project, var, value)
        db.commit()
        db.refresh(db_project)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Something went wrong : {e}")

    return db_project


def delete_project(db: Session, project_id: int) -> bool:
    """
    Deletes a project

    Args:
        db (Session): A database session
        project_id (int): The id of the project to delete

    Returns:
        A boolean indicating if the project was deleted
    """
    db_project = db.query(Project).filter_by(id=project_id).first()
    if db_project is not None:
        db.delete(db_project)
        db.commit()
        return True


    return False


def get_projects(db: Session, skip: int=0, limit:int=100) -> List[Project]:
    """
    Returns a list of all the projects

    Args:
        db (Session): A database session
        skip (int, optional): The number of projects to skip at the beginning of the list.
        limit (int, optional): The maximum number of projects to return

    Returns:
        A list of all the projects
    """
    return db.query(Project).offset(skip).limit(limit).all()


def get_project_by_id(db: Session, project_id: int) -> Optional[Project]:
    """
    Returns a specific project

    Args:
        db (Session): A database session
        project_id (int): The id of the project to retrieve

    Raises:
        HTTPException: The project cannot be found

    Returns:
        The project
    """
    db_project = db.query(Project).filter_by(id=project_id).first()

    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return db_project