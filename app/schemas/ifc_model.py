from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IFCModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    project_model_id: int
    revision: int
    number: int
    file_name: str
    saved_file_name: str
    description: str | None = None
    model_type: int = 0
    file_size: int = 0
    create_date: datetime | None = None
    regist_date: datetime | None = None


class UploadProgressResponse(BaseModel):
    file_name: str
    saved_file_name: str
    file_size: int
    chunks_written: int
    model: IFCModelResponse
