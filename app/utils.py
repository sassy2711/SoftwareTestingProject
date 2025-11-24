# app/utils.py


class EntityNotFoundError(Exception):
    """Raised when an entity is not found in the repository."""


class DuplicateEntityError(Exception):
    """Raised when attempting to insert a duplicate entity."""


class BusinessRuleViolationError(Exception):
    """Raised when a business rule is violated (e.g., over capacity)."""
