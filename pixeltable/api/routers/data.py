"""Data operations router for Pixeltable API."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Path, Query
import pixeltable as pxt
from pixeltable.api.models.data import (
    InsertRowRequest,
    InsertRowsRequest,
    QueryRequest,
    QueryResponse,
    UpdateRowRequest,
    UpdateRowsRequest,
    DeleteRowsRequest,
    WhereClause,
)

router = APIRouter(
    prefix="/tables/{table_name}",
    tags=["data"],
)


def _build_where_clause(table, where_clauses: Optional[List[WhereClause]]) -> Any:
    """Build Pixeltable where clause from WhereClause models."""
    if not where_clauses:
        return None
    
    conditions = []
    for clause in where_clauses:
        col = getattr(table, clause.column)
        
        if clause.operator == '=':
            conditions.append(col == clause.value)
        elif clause.operator == '!=':
            conditions.append(col != clause.value)
        elif clause.operator == '>':
            conditions.append(col > clause.value)
        elif clause.operator == '>=':
            conditions.append(col >= clause.value)
        elif clause.operator == '<':
            conditions.append(col < clause.value)
        elif clause.operator == '<=':
            conditions.append(col <= clause.value)
        elif clause.operator == 'like':
            conditions.append(col.contains(clause.value.replace('%', '')))
        elif clause.operator == 'in':
            conditions.append(col.isin(clause.value))
        elif clause.operator == 'not_in':
            conditions.append(~col.isin(clause.value))
        elif clause.operator == 'is_null':
            conditions.append(col.is_null())
        elif clause.operator == 'is_not_null':
            conditions.append(~col.is_null())
        else:
            raise ValueError(f"Unsupported operator: {clause.operator}")
    
    # Combine with AND logic
    if len(conditions) == 1:
        return conditions[0]
    else:
        result = conditions[0]
        for cond in conditions[1:]:
            result = result & cond
        return result


@router.post("/rows", summary="Insert a single row")
async def insert_row(
    table_name: str = Path(..., description="Name of the table"),
    request: InsertRowRequest = ...
) -> Dict[str, Any]:
    """Insert a single row into the table."""
    try:
        table = pxt.get_table(table_name)
        table.insert([request.data])
        return {"message": "Row inserted successfully", "data": request.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/rows/batch", summary="Insert multiple rows")
async def insert_rows(
    table_name: str = Path(..., description="Name of the table"),
    request: InsertRowsRequest = ...
) -> Dict[str, Any]:
    """Insert multiple rows into the table."""
    try:
        table = pxt.get_table(table_name)
        
        # Insert in batches if batch_size is specified
        if request.batch_size:
            for i in range(0, len(request.rows), request.batch_size):
                batch = request.rows[i:i + request.batch_size]
                table.insert(batch)
        else:
            table.insert(request.rows)
        
        return {
            "message": f"Successfully inserted {len(request.rows)} rows",
            "row_count": len(request.rows)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rows", summary="Query table data")
async def query_rows(
    table_name: str = Path(..., description="Name of the table"),
    select: Optional[str] = Query(None, description="Comma-separated column names"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum rows to return"),
    offset: int = Query(0, ge=0, description="Number of rows to skip"),
) -> QueryResponse:
    """Query rows from the table with basic filtering."""
    try:
        table = pxt.get_table(table_name)
        
        # Build query
        query = table
        
        # Select specific columns if specified
        if select:
            columns = [col.strip() for col in select.split(',')]
            query = query.select(*[getattr(table, col) for col in columns])
        
        # Apply limit and offset
        query = query.limit(limit)
        if offset > 0:
            # Pixeltable doesn't have direct offset, so we'll handle it differently
            # For now, we'll collect all and slice (not optimal for large datasets)
            all_rows = query.collect()
            rows = all_rows[offset:offset + limit]
        else:
            rows = query.collect()
        
        # Convert to list of dicts
        result_rows = []
        for row in rows:
            row_dict = {}
            for key in row._asdict().keys():
                value = getattr(row, key)
                # Handle special types
                if hasattr(value, '__dict__'):
                    row_dict[key] = str(value)
                else:
                    row_dict[key] = value
            result_rows.append(row_dict)
        
        return QueryResponse(
            rows=result_rows,
            has_more=len(result_rows) == limit,
            next_offset=offset + len(result_rows) if len(result_rows) == limit else None
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/query", summary="Advanced query with filtering")
async def query_rows_advanced(
    table_name: str = Path(..., description="Name of the table"),
    request: QueryRequest = ...
) -> QueryResponse:
    """Query rows with advanced filtering, sorting, and pagination."""
    try:
        table = pxt.get_table(table_name)
        
        # Build query
        query = table
        
        # Apply where clause
        if request.where:
            where_clause = _build_where_clause(table, request.where)
            if where_clause is not None:
                query = query.where(where_clause)
        
        # Select specific columns
        if request.select:
            query = query.select(*[getattr(table, col) for col in request.select])
        
        # Apply sorting
        if request.order_by:
            for order in request.order_by:
                col = getattr(table, order.column)
                query = query.order_by(col, asc=(order.direction == 'asc'))
        
        # Apply limit
        query = query.limit(request.limit)
        
        # Collect results
        rows = query.collect()
        
        # Handle offset manually (Pixeltable limitation)
        if request.offset > 0:
            rows = rows[request.offset:request.offset + request.limit]
        
        # Convert to list of dicts
        result_rows = []
        for row in rows:
            row_dict = {}
            for key in row._asdict().keys():
                value = getattr(row, key)
                # Handle special types
                if hasattr(value, '__dict__'):
                    row_dict[key] = str(value)
                else:
                    row_dict[key] = value
            result_rows.append(row_dict)
        
        return QueryResponse(
            rows=result_rows,
            has_more=len(result_rows) == request.limit,
            next_offset=request.offset + len(result_rows) if len(result_rows) == request.limit else None
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/rows/{row_id}", summary="Update a single row")
async def update_row(
    table_name: str = Path(..., description="Name of the table"),
    row_id: str = Path(..., description="Row identifier"),
    request: UpdateRowRequest = ...
) -> Dict[str, Any]:
    """Update a single row by ID."""
    try:
        table = pxt.get_table(table_name)
        
        # Pixeltable doesn't have direct row update by ID yet
        # This is a placeholder for when it's available
        # For now, we'll return a message indicating the limitation
        
        return {
            "message": "Row update by ID not yet implemented in Pixeltable core",
            "row_id": row_id,
            "data": request.data,
            "note": "Use batch update with where clause instead"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/rows", summary="Update multiple rows")
async def update_rows(
    table_name: str = Path(..., description="Name of the table"),
    request: UpdateRowsRequest = ...
) -> Dict[str, Any]:
    """Update multiple rows matching the where clause."""
    try:
        table = pxt.get_table(table_name)
        
        # Build where clause
        where_clause = _build_where_clause(table, request.where)
        
        # Pixeltable's update syntax
        update_dict = {}
        for col_name, value in request.set.items():
            update_dict[getattr(table, col_name)] = value
        
        # Apply update
        if where_clause is not None:
            table.update(update_dict, where=where_clause)
        else:
            table.update(update_dict)
        
        return {
            "message": "Rows updated successfully",
            "updated_fields": list(request.set.keys())
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/rows/{row_id}", summary="Delete a single row")
async def delete_row(
    table_name: str = Path(..., description="Name of the table"),
    row_id: str = Path(..., description="Row identifier"),
) -> Dict[str, Any]:
    """Delete a single row by ID."""
    try:
        table = pxt.get_table(table_name)
        
        # Pixeltable doesn't have direct row deletion by ID yet
        # This is a placeholder for when it's available
        
        return {
            "message": "Row deletion by ID not yet implemented in Pixeltable core",
            "row_id": row_id,
            "note": "Use batch delete with where clause instead"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/rows", summary="Delete multiple rows")
async def delete_rows(
    table_name: str = Path(..., description="Name of the table"),
    request: DeleteRowsRequest = ...
) -> Dict[str, Any]:
    """Delete rows matching the where clause."""
    try:
        table = pxt.get_table(table_name)
        
        # Build where clause
        if request.where:
            where_clause = _build_where_clause(table, request.where)
            # Get count before deletion
            count_query = table.where(where_clause) if where_clause else table
            # Note: Pixeltable doesn't have a direct count method, 
            # so we'd need to collect and count (inefficient for large datasets)
            
            # Pixeltable's delete syntax
            if where_clause is not None:
                table.delete(where=where_clause)
            else:
                # Delete all rows (be careful!)
                table.delete()
            
            return {
                "message": "Rows deleted successfully",
                "soft_delete": request.soft_delete
            }
        else:
            # Delete all rows if no where clause
            table.delete()
            return {
                "message": "All rows deleted successfully",
                "soft_delete": request.soft_delete
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rows/count", summary="Count rows in table")
async def count_rows(
    table_name: str = Path(..., description="Name of the table"),
) -> Dict[str, Any]:
    """Get the count of rows in the table."""
    try:
        table = pxt.get_table(table_name)
        
        # Pixeltable doesn't have a direct count method
        # We'll need to collect all and count (not optimal)
        # This is a limitation that should be addressed in Pixeltable core
        rows = table.collect()
        count = len(rows)
        
        return {
            "table_name": table_name,
            "row_count": count
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))