from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .. import crud, schemas, database

router = APIRouter(
    prefix="/operators",
    tags=["operators"],
)

@router.post("/", response_model=schemas.Operator)
async def create_operator(operator: schemas.OperatorCreate, db: AsyncSession = Depends(database.get_db)):
    return await crud.create_operator(db=db, operator=operator)

@router.get("/", response_model=List[schemas.Operator])
async def read_operators(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(database.get_db)):
    operators = await crud.get_operators(db, skip=skip, limit=limit)
    return operators

@router.patch("/{operator_id}", response_model=schemas.Operator)
async def update_operator(operator_id: int, is_active: bool, workload_limit: int, db: AsyncSession = Depends(database.get_db)):
    operator = await crud.update_operator(db, operator_id, is_active, workload_limit)
    if operator is None:
        raise HTTPException(status_code=404, detail="Operator not found")
    return operator
