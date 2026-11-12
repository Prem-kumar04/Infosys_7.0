
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.role_permission import RolePermission
from app.models.permission import Permission


async def user_has_permission(
    user: User,
    permission_name: str,
    db: AsyncSession,
) -> bool:
    # Users without an assigned role have no permissions
    if user.role_id is None:
        return False

    # Check whether the user's role has the requested permission
    result = await db.execute(
        select(Permission.id)
        .join(
            RolePermission,
            RolePermission.permission_id == Permission.id,
        )
        .where(
            RolePermission.role_id == user.role_id,
            Permission.name == permission_name,
        )
    )

    permission = result.scalar_one_or_none()

    return permission is not None
