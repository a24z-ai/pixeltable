"""Table management models for Pixeltable API."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ColumnInfo(BaseModel):
    """Information about a table column."""
    name: str = Field(..., description="Column name")
    type: str = Field(..., description="Column type")
    is_computed: bool = Field(False, description="Whether this is a computed column")
    nullable: Optional[bool] = Field(True, description="Whether column allows null values")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"name": "id", "type": "int", "is_computed": False, "nullable": False},
                {"name": "thumbnail", "type": "image", "is_computed": True, "nullable": True}
            ]
        }
    )


class TableSchema(BaseModel):
    """Schema definition for a table."""
    columns: Dict[str, str] = Field(..., description="Column name to type mapping")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "columns": {
                        "id": "int",
                        "name": "string",
                        "email": "string",
                        "profile_image": "image",
                        "metadata": "json"
                    }
                }
            ]
        }
    )


class CreateTableRequest(BaseModel):
    """Request to create a new table."""
    name: str = Field(..., description="Table name", pattern="^[a-zA-Z][a-zA-Z0-9_]*$")
    schema: TableSchema = Field(..., description="Table schema definition")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "users",
                    "schema": {
                        "columns": {
                            "id": "int",
                            "name": "string",
                            "email": "string",
                            "created_at": "timestamp"
                        }
                    }
                }
            ]
        }
    )


class TableInfo(BaseModel):
    """Information about a table."""
    name: str = Field(..., description="Table name")
    column_count: int = Field(..., description="Number of columns")
    row_count: Optional[int] = Field(None, description="Number of rows in table")
    columns: List[ColumnInfo] = Field(..., description="Column information")
    created_at: Optional[str] = Field(None, description="Table creation timestamp")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "users",
                    "column_count": 5,
                    "row_count": 1234,
                    "columns": [
                        {"name": "id", "type": "int", "is_computed": False},
                        {"name": "name", "type": "string", "is_computed": False},
                        {"name": "email", "type": "string", "is_computed": False},
                        {"name": "profile_image", "type": "image", "is_computed": False},
                        {"name": "thumbnail", "type": "image", "is_computed": True}
                    ],
                    "created_at": "2025-01-10T12:00:00Z"
                }
            ]
        }
    )