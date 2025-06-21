from enum import StrEnum


class UserRole(StrEnum):
    MANAGER = "manager"
    ADMIN = "admin"
    PUBLICATIONS_MANAGER = "publications_manager"