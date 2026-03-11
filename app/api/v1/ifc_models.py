"""
IFC 모델 파일 업로드/다운로드 API

Spring Boot 대비 개선사항:
- 업로드: MultipartFile.getBytes() 전량 적재 → chunk 단위 비동기 스트리밍
- 다운로드: Resource 전체 응답 → StreamingResponse (async generator)
- 메모리 사용량이 파일 크기와 무관하게 일정 (chunk_size만큼만 점유)
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, Response, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.exceptions import BadRequestException, NotFoundException
from app.db.session import get_db
from app.models.ifc_model import IFCModel
from app.schemas.ifc_model import IFCModelResponse, UploadProgressResponse
from app.services.file_service import (
    delete_file,
    get_file_size,
    save_file_chunked,
    stream_file,
)

logger = logging.getLogger("rpms")

router = APIRouter(tags=["IFC Models"])

ALLOWED_EXTENSIONS = {".ifc", ".ifczip", ".zip", ".rpms"}


def _validate_extension(filename: str) -> None:
    from pathlib import Path

    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise BadRequestException(
            f"Unsupported file type: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )


@router.post(
    "/projects/{project_id}/models/upload",
    response_model=UploadProgressResponse,
    status_code=status.HTTP_201_CREATED,
    summary="IFC 모델 파일 업로드 (스트리밍)",
    description=(
        "대용량 IFC 파일을 chunk 단위로 비동기 스트리밍 저장합니다. "
        "파일 전체를 메모리에 올리지 않아 수 GB 파일도 안정적으로 처리됩니다."
    ),
)
async def upload_model(
    project_id: int,
    file: UploadFile = File(...),
    project_model_id: int = Form(...),
    revision: int = Form(0),
    number: int = Form(0),
    description: str = Form(""),
    model_type: int = Form(0),
    response: Response = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    if not file.filename:
        raise BadRequestException("File is required")

    _validate_extension(file.filename)

    original_name, saved_name, total_bytes, chunks = await save_file_chunked(
        upload_file=file,
        project_id=project_id,
        project_model_id=project_model_id,
        revision=revision,
        number=number,
    )

    db_model = IFCModel(
        project_id=project_id,
        project_model_id=project_model_id,
        revision=revision,
        number=number,
        file_name=original_name,
        saved_file_name=saved_name,
        description=description,
        model_type=model_type,
        file_size=total_bytes,
        create_date=datetime.now(),
    )
    db.add(db_model)
    db.commit()
    db.refresh(db_model)

    if response:
        response.headers["Location"] = (
            f"/api/v1/projects/{project_id}/models/{db_model.id}"
        )

    logger.info(
        "Upload complete: %s (%d bytes, %d chunks) by user %s",
        original_name,
        total_bytes,
        chunks,
        user.get("email"),
    )

    return UploadProgressResponse(
        file_name=original_name,
        saved_file_name=saved_name,
        file_size=total_bytes,
        chunks_written=chunks,
        model=IFCModelResponse.model_validate(db_model),
    )


@router.get(
    "/models/{model_id}/download",
    summary="IFC 모델 파일 다운로드 (스트리밍)",
    description=(
        "async generator 기반 StreamingResponse로 파일을 전송합니다. "
        "서버 메모리에 전체 파일을 올리지 않습니다."
    ),
)
async def download_model(
    model_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    model = db.get(IFCModel, model_id)
    if not model:
        raise NotFoundException("IFCModel", model_id)

    file_size = get_file_size(model.project_id, model.saved_file_name)
    if file_size == 0:
        raise NotFoundException("File", model.saved_file_name)

    return StreamingResponse(
        content=stream_file(model.project_id, model.saved_file_name),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{model.file_name}"',
            "Content-Length": str(file_size),
            "X-Chunk-Size": str(settings.FILE_CHUNK_SIZE),
        },
    )


@router.get(
    "/projects/{project_id}/models",
    response_model=list[IFCModelResponse],
    summary="프로젝트 IFC 모델 목록 조회",
)
def list_models(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    stmt = (
        select(IFCModel)
        .where(IFCModel.project_id == project_id)
        .order_by(IFCModel.regist_date.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


@router.delete(
    "/models/{model_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="IFC 모델 삭제",
)
def delete_model(
    model_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    model = db.get(IFCModel, model_id)
    if not model:
        raise NotFoundException("IFCModel", model_id)

    delete_file(model.project_id, model.saved_file_name)
    db.delete(model)
    db.commit()
