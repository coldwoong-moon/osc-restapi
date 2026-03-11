from fastapi import APIRouter

from app.api.v1 import (
    apartment_complexes,
    assemblies,
    auth,
    boms,
    cranes,
    drawings,
    floors,
    health,
    ifc_models,
    misc,
    parts,
    projects,
    users,
    zones,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(users.router)
api_router.include_router(apartment_complexes.router)
api_router.include_router(floors.router)
api_router.include_router(zones.router)
api_router.include_router(assemblies.router)
api_router.include_router(parts.router)
api_router.include_router(boms.router)
api_router.include_router(cranes.router)
api_router.include_router(drawings.router)
api_router.include_router(ifc_models.router)
api_router.include_router(misc.router)
