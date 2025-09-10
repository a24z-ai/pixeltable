"""Table management endpoints."""

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
import pixeltable as pxt

from pixeltable.api.models.tables import (
    TableSchema,
    CreateTableRequest,
    TableInfo,
    ColumnInfo,
)

router = APIRouter()


@router.get("/tables")
async def list_tables() -> List[str]:
    """List all tables in Pixeltable."""
    try:
        tables = pxt.list_tables()
        return [str(table) for table in tables]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tables")
async def create_table(request: CreateTableRequest) -> Dict[str, str]:
    """Create a new table."""
    try:
        # Map string type names to Pixeltable types
        type_mapping = {
            "string": pxt.String,
            "int": pxt.Int,
            "float": pxt.Float,
            "bool": pxt.Bool,
            "json": pxt.Json,
            "timestamp": pxt.Timestamp,
            "image": pxt.Image,
            "video": pxt.Video,
            "audio": pxt.Audio,
            "document": pxt.Document,
        }
        
        schema = {}
        for col_name, type_name in request.schema.columns.items():
            if type_name.lower() not in type_mapping:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unknown type: {type_name}. Valid types: {list(type_mapping.keys())}"
                )
            schema[col_name] = type_mapping[type_name.lower()]
        
        table = pxt.create_table(request.name, schema=schema)
        return {"message": f"Table '{request.name}' created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tables/{table_name}")
async def get_table_info(table_name: str) -> TableInfo:
    """Get information about a specific table."""
    try:
        table = pxt.get_table(table_name)
        columns = []
        for col in table.columns():
            columns.append(ColumnInfo(
                name=col.name,
                type=str(col.col_type),
                is_computed=col.is_computed,
                nullable=True  # Pixeltable doesn't expose this yet
            ))
        
        # Try to get row count (might be expensive for large tables)
        try:
            rows = table.collect()
            row_count = len(rows)
        except:
            row_count = None
        
        return TableInfo(
            name=table_name,
            column_count=len(columns),
            row_count=row_count,
            columns=columns
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Table not found: {str(e)}")


@router.delete("/tables/{table_name}")
async def drop_table(table_name: str) -> Dict[str, str]:
    """Drop a table."""
    try:
        pxt.drop_table(table_name)
        return {"message": f"Table '{table_name}' dropped successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)}