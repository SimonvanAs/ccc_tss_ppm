# TSS PPM v3.0 - Admin Router
"""API endpoints for admin operations."""

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException

from src.auth import CurrentUser, require_admin
from src.services.keycloak_admin import KeycloakAdminService, KeycloakAdminError
from src.schemas.admin import (
    AdminUserResponse,
    UpdateRolesRequest,
    UpdateManagerRequest,
    UpdateStatusRequest,
    BulkOperationRequest,
    BulkOperationResponse,
)

router = APIRouter(prefix='/api/v1/admin', tags=['Admin'])


def get_keycloak_admin() -> KeycloakAdminService:
    """Dependency for Keycloak Admin Service."""
    return KeycloakAdminService()


def keycloak_user_to_response(
    user: dict,
    roles: List[dict],
) -> AdminUserResponse:
    """Convert Keycloak user dict to response model."""
    attributes = user.get('attributes', {})
    return AdminUserResponse(
        id=user['id'],
        email=user.get('email', ''),
        first_name=user.get('firstName'),
        last_name=user.get('lastName'),
        enabled=user.get('enabled', False),
        roles=[r['name'] for r in roles],
        function_title=attributes.get('function_title', [None])[0],
        tov_level=attributes.get('tov_level', [None])[0],
        manager_id=attributes.get('manager_id', [None])[0],
        opco_id=attributes.get('opco_id', [None])[0],
    )


@router.get('/users', response_model=List[AdminUserResponse])
async def list_users(
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    keycloak: Annotated[KeycloakAdminService, Depends(get_keycloak_admin)],
    search: Annotated[Optional[str], Query(description='Search by name/email')] = None,
    role: Annotated[Optional[str], Query(description='Filter by role')] = None,
    enabled: Annotated[Optional[bool], Query(description='Filter by status')] = None,
    first: Annotated[int, Query(description='Pagination offset', ge=0)] = 0,
    max_results: Annotated[int, Query(description='Max results', ge=1, le=100)] = 50,
) -> List[AdminUserResponse]:
    """List users in the OpCo.

    Args:
        current_user: The authenticated admin user
        keycloak: Keycloak Admin Service
        search: Search term for name/email
        role: Filter by role
        enabled: Filter by enabled status
        first: Pagination offset
        max_results: Maximum number of results

    Returns:
        List of users with their details and roles
    """
    try:
        users = await keycloak.get_users(
            opco_id=current_user.opco_id,
            search=search,
            first=first,
            max_results=max_results,
        )

        result = []
        for user in users:
            roles = await keycloak.get_user_roles(user['id'])
            response = keycloak_user_to_response(user, roles)

            # Apply filters
            if role and role not in response.roles:
                continue
            if enabled is not None and response.enabled != enabled:
                continue

            result.append(response)

        return result

    except KeycloakAdminError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/users/{user_id}', response_model=AdminUserResponse)
async def get_user(
    user_id: str,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    keycloak: Annotated[KeycloakAdminService, Depends(get_keycloak_admin)],
) -> AdminUserResponse:
    """Get user details by ID.

    Args:
        user_id: The Keycloak user ID
        current_user: The authenticated admin user
        keycloak: Keycloak Admin Service

    Returns:
        User details with roles
    """
    try:
        user = await keycloak.get_user(user_id)
        roles = await keycloak.get_user_roles(user_id)
        return keycloak_user_to_response(user, roles)

    except KeycloakAdminError as e:
        if 'not found' in str(e).lower():
            raise HTTPException(status_code=404, detail='User not found')
        raise HTTPException(status_code=500, detail=str(e))


@router.put('/users/{user_id}/roles')
async def update_user_roles(
    user_id: str,
    request: UpdateRolesRequest,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    keycloak: Annotated[KeycloakAdminService, Depends(get_keycloak_admin)],
) -> dict:
    """Update user's roles.

    Args:
        user_id: The Keycloak user ID
        request: The roles to set
        current_user: The authenticated admin user
        keycloak: Keycloak Admin Service

    Returns:
        Success message
    """
    try:
        # Get current roles
        current_roles = await keycloak.get_user_roles(user_id)
        current_role_names = {r['name'] for r in current_roles}
        new_role_names = set(request.roles)

        # Calculate roles to add and remove
        to_add = new_role_names - current_role_names
        to_remove = current_role_names - new_role_names

        # Filter out default Keycloak roles that shouldn't be modified
        protected_roles = {'default-roles-tss-ppm', 'offline_access', 'uma_authorization'}
        to_add -= protected_roles
        to_remove -= protected_roles

        # Apply changes
        for role_name in to_add:
            await keycloak.assign_role(user_id, role_name)

        for role_name in to_remove:
            await keycloak.remove_role(user_id, role_name)

        return {'message': 'Roles updated successfully'}

    except KeycloakAdminError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put('/users/{user_id}/manager')
async def update_user_manager(
    user_id: str,
    request: UpdateManagerRequest,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    keycloak: Annotated[KeycloakAdminService, Depends(get_keycloak_admin)],
) -> dict:
    """Update user's manager.

    Args:
        user_id: The Keycloak user ID
        request: The new manager ID
        current_user: The authenticated admin user
        keycloak: Keycloak Admin Service

    Returns:
        Success message
    """
    try:
        await keycloak.update_user_manager(user_id, request.manager_id)
        return {'message': 'Manager updated successfully'}

    except KeycloakAdminError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put('/users/{user_id}/status')
async def update_user_status(
    user_id: str,
    request: UpdateStatusRequest,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    keycloak: Annotated[KeycloakAdminService, Depends(get_keycloak_admin)],
) -> dict:
    """Enable or disable a user.

    Args:
        user_id: The Keycloak user ID
        request: The new status
        current_user: The authenticated admin user
        keycloak: Keycloak Admin Service

    Returns:
        Success message
    """
    try:
        if request.enabled:
            await keycloak.enable_user(user_id)
        else:
            await keycloak.disable_user(user_id)

        return {'message': f"User {'enabled' if request.enabled else 'disabled'} successfully"}

    except KeycloakAdminError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/users/bulk', response_model=BulkOperationResponse)
async def bulk_operation(
    request: BulkOperationRequest,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    keycloak: Annotated[KeycloakAdminService, Depends(get_keycloak_admin)],
) -> BulkOperationResponse:
    """Perform bulk operations on multiple users.

    Supported operations:
    - assign_role: Assign a role to all users
    - remove_role: Remove a role from all users
    - assign_manager: Set the same manager for all users

    Args:
        request: The bulk operation request
        current_user: The authenticated admin user
        keycloak: Keycloak Admin Service

    Returns:
        Summary of the operation
    """
    processed = 0
    failed = 0
    errors = []

    for user_id in request.user_ids:
        try:
            if request.operation == 'assign_role':
                if not request.role:
                    raise ValueError('Role is required for assign_role operation')
                await keycloak.assign_role(user_id, request.role)
            elif request.operation == 'remove_role':
                if not request.role:
                    raise ValueError('Role is required for remove_role operation')
                await keycloak.remove_role(user_id, request.role)
            elif request.operation == 'assign_manager':
                if not request.manager_id:
                    raise ValueError('Manager ID is required for assign_manager operation')
                await keycloak.update_user_manager(user_id, request.manager_id)
            else:
                raise ValueError(f'Unknown operation: {request.operation}')

            processed += 1

        except Exception as e:
            failed += 1
            errors.append(f'{user_id}: {str(e)}')

    return BulkOperationResponse(
        processed=processed,
        failed=failed,
        errors=errors,
    )
