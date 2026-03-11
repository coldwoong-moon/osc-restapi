from app.crud.base import CRUDBase
from app.models.project import Project, ProjectModel
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectModelCreate, ProjectModelUpdate


class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    pass


class CRUDProjectModel(CRUDBase[ProjectModel, ProjectModelCreate, ProjectModelUpdate]):
    pass


project = CRUDProject(Project)
project_model = CRUDProjectModel(ProjectModel)
