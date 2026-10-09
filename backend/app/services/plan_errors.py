"""Typed domain errors so the API layer can map failures to clear status codes."""

from __future__ import annotations


class PlanError(Exception):
    """Base class for plan domain errors."""


class TerritoryNotFoundError(PlanError):
    pass


class AccountNotFoundError(PlanError):
    pass


class UnauthorizedError(PlanError):
    pass


class PlanNotFoundError(PlanError):
    pass


class InvalidPlanStateError(PlanError):
    pass


class NoApprovedItemsError(PlanError):
    pass


class RetrievalUnavailableError(PlanError):
    """Raised when a data source cannot be reached; callers retry or fail safe."""
