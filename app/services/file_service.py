"""
대용량 파일 스트리밍 서비스

기존 Spring Boot의 MultipartFile.getBytes() 방식은 파일 전체를 메모리에 적재하여
대용량 IFC 파일(수백 MB ~ 수 GB)에서 OOM을 유발했다.

개선:
- 업로드: chunk 단위 비동기 읽기/쓰기 → 메모리 사용량이 파일 크기와 무관
- 다운로드: async generator 기반 StreamingResponse → 전체 파일 로딩 없이 전송
- 파일 크기와 관계없이 일정한 메모리 사용 (chunk_size만큼만 점유)
"""

import logging
import os
import secrets
from pathlib import Path
from typing import AsyncGenerator

import aiofiles
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import BadRequestException

logger = logging.getLogger("rpms")


def _ensure_directory(directory: str) -> Path:
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _generate_saved_filename(
    project_model_id: int, revision: int, number: int, original_filename: str
) -> str:
    stem = Path(original_filename).stem
    suffix = Path(original_filename).suffix
    random_part = secrets.token_hex(5)
    return f"{project_model_id}_{revision}_{number}_{stem}_{random_part}{suffix}"


async def save_file_chunked(
    upload_file: UploadFile,
    project_id: int,
    project_model_id: int,
    revision: int,
    number: int,
) -> tuple[str, str, int, int]:
    """
    청크 단위 비동기 파일 저장.

    Returns:
        (original_filename, saved_filename, total_bytes, chunks_written)
    """
    original_filename = upload_file.filename or "unknown"
    saved_filename = _generate_saved_filename(
        project_model_id, revision, number, original_filename
    )

    directory = _ensure_directory(
        os.path.join(settings.FILE_STORAGE_PATH, "model", str(project_id))
    )
    file_path = directory / saved_filename

    chunk_size = settings.FILE_CHUNK_SIZE
    total_bytes = 0
    chunks_written = 0

    async with aiofiles.open(file_path, "wb") as f:
        while True:
            chunk = await upload_file.read(chunk_size)
            if not chunk:
                break
            await f.write(chunk)
            total_bytes += len(chunk)
            chunks_written += 1

            if total_bytes > settings.FILE_MAX_SIZE:
                await f.close()
                file_path.unlink(missing_ok=True)
                raise BadRequestException(
                    f"File exceeds maximum size: {settings.FILE_MAX_SIZE} bytes"
                )

    logger.info(
        "File saved: %s (%d bytes, %d chunks)", saved_filename, total_bytes, chunks_written
    )
    return original_filename, saved_filename, total_bytes, chunks_written


async def stream_file(
    project_id: int, saved_filename: str
) -> AsyncGenerator[bytes, None]:
    """
    비동기 generator 기반 파일 스트리밍.

    StreamingResponse와 함께 사용하여 전체 파일을 메모리에 올리지 않고 전송한다.
    """
    file_path = Path(
        settings.FILE_STORAGE_PATH, "model", str(project_id), saved_filename
    )

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {saved_filename}")

    chunk_size = settings.FILE_CHUNK_SIZE

    async with aiofiles.open(file_path, "rb") as f:
        while True:
            chunk = await f.read(chunk_size)
            if not chunk:
                break
            yield chunk


def get_file_size(project_id: int, saved_filename: str) -> int:
    file_path = Path(
        settings.FILE_STORAGE_PATH, "model", str(project_id), saved_filename
    )
    if not file_path.exists():
        return 0
    return file_path.stat().st_size


def delete_file(project_id: int, saved_filename: str) -> bool:
    file_path = Path(
        settings.FILE_STORAGE_PATH, "model", str(project_id), saved_filename
    )
    if file_path.exists():
        file_path.unlink()
        return True
    return False
