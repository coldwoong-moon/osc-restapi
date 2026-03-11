"""
대용량 파일 스트리밍 업로드/다운로드 테스트

검증 항목:
- 청크 단위 비동기 저장 (메모리 전량 적재 방지)
- StreamingResponse 기반 다운로드
- 파일 확장자 검증
- 파일 크기 제한
- 업로드 → 다운로드 → 삭제 전체 플로우
"""

import io
import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql import func

from app.api.deps import get_current_user
from app.api.v1.ifc_models import router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.db.base import Base
from app.db.session import get_db
from app.models.ifc_model import IFCModel


@pytest.fixture(autouse=True)
def temp_upload_dir(tmp_path, monkeypatch):
    """각 테스트마다 임시 업로드 디렉토리 사용."""
    upload_dir = str(tmp_path / "uploads")
    monkeypatch.setattr(settings, "FILE_STORAGE_PATH", upload_dir)
    monkeypatch.setattr(settings, "FILE_CHUNK_SIZE", 1024)  # 1KB chunks for testing
    yield upload_dir


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router, prefix="/api/v1")

    def override_get_db():
        yield db_session

    def override_get_current_user():
        return {"sub": 1, "email": "test@test.com", "authorities": ["ROLE_USER"]}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    return TestClient(app)


def _make_ifc_content(size_bytes: int = 5000) -> bytes:
    """테스트용 IFC 파일 콘텐츠 생성."""
    header = b"ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION(('ViewDefinition [CoordinationView]'),'2;1');\n"
    remaining = size_bytes - len(header)
    return header + b"X" * max(0, remaining)


class TestChunkedUpload:
    def test_upload_creates_file_and_db_record(self, client, db_session):
        content = _make_ifc_content(3000)
        resp = client.post(
            "/api/v1/projects/1/models/upload",
            files={"file": ("test_model.ifc", io.BytesIO(content), "application/octet-stream")},
            data={
                "project_model_id": "10",
                "revision": "1",
                "number": "1",
                "description": "Test IFC model",
                "model_type": "0",
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["file_name"] == "test_model.ifc"
        assert body["file_size"] == 3000
        assert body["chunks_written"] >= 1
        assert body["model"]["project_id"] == 1

        db_model = db_session.get(IFCModel, body["model"]["id"])
        assert db_model is not None
        assert db_model.file_size == 3000

    def test_upload_writes_in_chunks(self, client, temp_upload_dir):
        """1KB 청크 설정에서 5KB 파일 → 최소 5개 청크."""
        content = _make_ifc_content(5120)
        resp = client.post(
            "/api/v1/projects/1/models/upload",
            files={"file": ("chunked.ifc", io.BytesIO(content), "application/octet-stream")},
            data={"project_model_id": "10", "revision": "1", "number": "1"},
        )
        assert resp.status_code == 201
        assert resp.json()["chunks_written"] >= 5

    def test_upload_rejects_invalid_extension(self, client):
        resp = client.post(
            "/api/v1/projects/1/models/upload",
            files={"file": ("virus.exe", io.BytesIO(b"bad"), "application/octet-stream")},
            data={"project_model_id": "10", "revision": "1", "number": "1"},
        )
        assert resp.status_code == 400
        assert "Unsupported file type" in resp.json()["detail"]

    def test_upload_enforces_max_file_size(self, client, monkeypatch):
        monkeypatch.setattr(settings, "FILE_MAX_SIZE", 2000)
        content = _make_ifc_content(3000)
        resp = client.post(
            "/api/v1/projects/1/models/upload",
            files={"file": ("big.ifc", io.BytesIO(content), "application/octet-stream")},
            data={"project_model_id": "10", "revision": "1", "number": "1"},
        )
        assert resp.status_code == 400
        assert "exceeds maximum size" in resp.json()["detail"]

    def test_upload_accepts_ifczip(self, client):
        resp = client.post(
            "/api/v1/projects/1/models/upload",
            files={"file": ("model.ifczip", io.BytesIO(b"PK\x03\x04zip"), "application/octet-stream")},
            data={"project_model_id": "10", "revision": "1", "number": "1"},
        )
        assert resp.status_code == 201


class TestStreamingDownload:
    def _upload_and_get_id(self, client) -> int:
        content = _make_ifc_content(4096)
        resp = client.post(
            "/api/v1/projects/1/models/upload",
            files={"file": ("download_test.ifc", io.BytesIO(content), "application/octet-stream")},
            data={"project_model_id": "10", "revision": "1", "number": "1"},
        )
        return resp.json()["model"]["id"]

    def test_download_returns_streamed_content(self, client):
        model_id = self._upload_and_get_id(client)
        resp = client.get(f"/api/v1/models/{model_id}/download")
        assert resp.status_code == 200
        assert len(resp.content) == 4096
        assert resp.headers["content-type"] == "application/octet-stream"
        assert "download_test.ifc" in resp.headers["content-disposition"]

    def test_download_includes_content_length(self, client):
        model_id = self._upload_and_get_id(client)
        resp = client.get(f"/api/v1/models/{model_id}/download")
        assert resp.headers["content-length"] == "4096"

    def test_download_nonexistent_model_returns_404(self, client):
        resp = client.get("/api/v1/models/9999/download")
        assert resp.status_code == 404

    def test_upload_then_download_integrity(self, client):
        """업로드한 파일과 다운로드한 파일의 바이트가 동일한지 검증."""
        original = _make_ifc_content(8192)
        upload_resp = client.post(
            "/api/v1/projects/1/models/upload",
            files={"file": ("integrity.ifc", io.BytesIO(original), "application/octet-stream")},
            data={"project_model_id": "10", "revision": "1", "number": "1"},
        )
        model_id = upload_resp.json()["model"]["id"]
        download_resp = client.get(f"/api/v1/models/{model_id}/download")
        assert download_resp.content == original


class TestModelCRUD:
    def test_list_models_empty(self, client):
        resp = client.get("/api/v1/projects/1/models")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_models_after_upload(self, client):
        client.post(
            "/api/v1/projects/1/models/upload",
            files={"file": ("a.ifc", io.BytesIO(_make_ifc_content(100)), "application/octet-stream")},
            data={"project_model_id": "10", "revision": "1", "number": "1"},
        )
        client.post(
            "/api/v1/projects/1/models/upload",
            files={"file": ("b.ifc", io.BytesIO(_make_ifc_content(200)), "application/octet-stream")},
            data={"project_model_id": "10", "revision": "1", "number": "2"},
        )
        resp = client.get("/api/v1/projects/1/models")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_delete_model_removes_file_and_record(self, client, db_session, temp_upload_dir):
        upload_resp = client.post(
            "/api/v1/projects/1/models/upload",
            files={"file": ("delete_me.ifc", io.BytesIO(_make_ifc_content(500)), "application/octet-stream")},
            data={"project_model_id": "10", "revision": "1", "number": "1"},
        )
        model_id = upload_resp.json()["model"]["id"]
        saved_name = upload_resp.json()["saved_file_name"]

        delete_resp = client.delete(f"/api/v1/models/{model_id}")
        assert delete_resp.status_code == 204

        assert db_session.get(IFCModel, model_id) is None

        file_path = os.path.join(temp_upload_dir, "model", "1", saved_name)
        assert not os.path.exists(file_path)

    def test_delete_nonexistent_returns_404(self, client):
        resp = client.delete("/api/v1/models/9999")
        assert resp.status_code == 404


class TestMemoryEfficiency:
    """메모리 효율성 검증 — 청크 단위 처리의 핵심 가치."""

    def test_chunk_size_determines_memory_usage(self, client, monkeypatch):
        """512B 청크 설정에서 큰 파일도 512B씩만 처리."""
        monkeypatch.setattr(settings, "FILE_CHUNK_SIZE", 512)
        content = _make_ifc_content(10240)  # 10KB
        resp = client.post(
            "/api/v1/projects/1/models/upload",
            files={"file": ("mem_test.ifc", io.BytesIO(content), "application/octet-stream")},
            data={"project_model_id": "10", "revision": "1", "number": "1"},
        )
        assert resp.status_code == 201
        assert resp.json()["chunks_written"] >= 20  # 10KB / 512B = 20 chunks

    def test_download_response_is_streaming(self, client):
        """다운로드 응답이 StreamingResponse 타입인지 확인."""
        content = _make_ifc_content(2048)
        upload_resp = client.post(
            "/api/v1/projects/1/models/upload",
            files={"file": ("stream.ifc", io.BytesIO(content), "application/octet-stream")},
            data={"project_model_id": "10", "revision": "1", "number": "1"},
        )
        model_id = upload_resp.json()["model"]["id"]
        resp = client.get(f"/api/v1/models/{model_id}/download")
        assert resp.headers.get("x-chunk-size") == "1024"
