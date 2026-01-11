# TSS PPM v3.0 - Admin Schemas
"""Pydantic models for admin API endpoints."""

from typing import List, Optional
from pydantic import BaseModel


class AdminUserResponse(BaseModel):
    """Response model for user information in admin context."""

    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    enabled: bool
    roles: List[str] = []
    function_title: Optional[str] = None
    tov_level: Optional[str] = None
    manager_id: Optional[str] = None
    opco_id: Optional[str] = None

    class Config:
        from_attributes = True


class UpdateRolesRequest(BaseModel):
    """Request model for updating user roles."""

    roles: List[str]


class UpdateManagerRequest(BaseModel):
    """Request model for updating user's manager."""

    manager_id: str


class UpdateStatusRequest(BaseModel):
    """Request model for updating user status."""

    enabled: bool


class BulkOperationRequest(BaseModel):
    """Request model for bulk operations."""

    user_ids: List[str]
    operation: str  # 'assign_role', 'remove_role', 'assign_manager'
    role: Optional[str] = None
    manager_id: Optional[str] = None


class BulkOperationResponse(BaseModel):
    """Response model for bulk operations."""

    processed: int
    failed: int = 0
    errors: List[str] = []
