from fastapi import Depends, HTTPException
from core.dependencies import get_current_user


def require_permission(permission_name: str):

    def permission_checker(user=Depends(get_current_user)):

        permissions = []

        for role in user.roles:
            for perm in role.permissions:
                permissions.append(perm.name)

        if permission_name not in permissions:
            raise HTTPException(status_code=403, detail="Permission denied")

        return user

    return permission_checker