"""Data operation models for Pixeltable API."""

from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field, ConfigDict


class RowData(BaseModel):
    """Represents a single row of data."""
    model_config = ConfigDict(extra='allow')
    
    def model_dump(self, **kwargs):
        """Override to get all fields including extras."""
        return {**super().model_dump(**kwargs), **self.__pydantic_extra__}


class InsertRowRequest(BaseModel):
    """Request to insert a single row."""
    data: Dict[str, Any] = Field(..., description="Column name to value mapping")


class InsertRowsRequest(BaseModel):
    """Request to insert multiple rows."""
    rows: List[Dict[str, Any]] = Field(..., description="List of rows to insert")
    batch_size: Optional[int] = Field(None, ge=1, le=1000, description="Batch size for insertion")


class WhereClause(BaseModel):
    """Where clause for filtering."""
    column: str = Field(..., description="Column name")
    operator: Literal['=', '!=', '>', '>=', '<', '<=', 'like', 'in', 'not_in', 'is_null', 'is_not_null'] = Field(..., description="Comparison operator")
    value: Optional[Any] = Field(None, description="Value to compare against")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"column": "age", "operator": ">", "value": 18},
                {"column": "name", "operator": "like", "value": "%smith%"},
                {"column": "status", "operator": "in", "value": ["active", "pending"]},
                {"column": "deleted_at", "operator": "is_null"}
            ]
        }
    )


class OrderByClause(BaseModel):
    """Order by clause for sorting."""
    column: str = Field(..., description="Column name to sort by")
    direction: Literal['asc', 'desc'] = Field('asc', description="Sort direction")


class PaginationParams(BaseModel):
    """Pagination parameters."""
    limit: int = Field(100, ge=1, le=1000, description="Number of rows to return")
    offset: int = Field(0, ge=0, description="Number of rows to skip")


class QueryRequest(BaseModel):
    """Request to query table data."""
    select: Optional[List[str]] = Field(None, description="Columns to select (None = all)")
    where: Optional[List[WhereClause]] = Field(None, description="Filter conditions (AND logic)")
    order_by: Optional[List[OrderByClause]] = Field(None, description="Sort order")
    limit: int = Field(100, ge=1, le=1000, description="Maximum rows to return")
    offset: int = Field(0, ge=0, description="Number of rows to skip")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "select": ["id", "name", "email"],
                    "where": [
                        {"column": "status", "operator": "=", "value": "active"},
                        {"column": "age", "operator": ">=", "value": 18}
                    ],
                    "order_by": [{"column": "created_at", "direction": "desc"}],
                    "limit": 50,
                    "offset": 0
                }
            ]
        }
    )


class QueryResponse(BaseModel):
    """Response from a query operation."""
    rows: List[Dict[str, Any]] = Field(..., description="Query result rows")
    total_count: Optional[int] = Field(None, description="Total count of matching rows (if requested)")
    has_more: bool = Field(..., description="Whether more rows are available")
    next_offset: Optional[int] = Field(None, description="Offset for next page")


class UpdateRowRequest(BaseModel):
    """Request to update a single row."""
    row_id: Union[str, int] = Field(..., description="Row identifier")
    data: Dict[str, Any] = Field(..., description="Column values to update")


class UpdateRowsRequest(BaseModel):
    """Request to update multiple rows."""
    where: List[WhereClause] = Field(..., description="Filter conditions for rows to update")
    set: Dict[str, Any] = Field(..., description="Column values to set")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "where": [{"column": "status", "operator": "=", "value": "pending"}],
                    "set": {"status": "active", "updated_at": "2025-01-10T12:00:00Z"}
                }
            ]
        }
    )


class DeleteRowsRequest(BaseModel):
    """Request to delete rows."""
    where: Optional[List[WhereClause]] = Field(None, description="Filter conditions (None = delete all)")
    soft_delete: bool = Field(False, description="Perform soft delete instead of hard delete")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "where": [{"column": "status", "operator": "=", "value": "archived"}],
                    "soft_delete": False
                }
            ]
        }
    )