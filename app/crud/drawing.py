from app.crud.base import CRUDBase
from app.models.drawing import DrawingTree, Drawing, ReferenceDrawing
from app.schemas.drawing import (
    DrawingTreeCreate,
    DrawingTreeUpdate,
    DrawingCreate,
    ReferenceDrawingCreate,
)


class CRUDDrawingTree(CRUDBase[DrawingTree, DrawingTreeCreate, DrawingTreeUpdate]):
    pass


class CRUDDrawing(CRUDBase[Drawing, DrawingCreate, DrawingCreate]):
    pass


class CRUDReferenceDrawing(CRUDBase[ReferenceDrawing, ReferenceDrawingCreate, ReferenceDrawingCreate]):
    pass


drawing_tree = CRUDDrawingTree(DrawingTree)
drawing = CRUDDrawing(Drawing)
reference_drawing = CRUDReferenceDrawing(ReferenceDrawing)
