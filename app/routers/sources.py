from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .. import crud, schemas, database

router = APIRouter(
    prefix="/sources",
    tags=["sources"],
)

@router.post("/", response_model=schemas.Source)
async def create_source(source: schemas.SourceCreate, db: AsyncSession = Depends(database.get_db)):
    return await crud.create_source(db=db, source=source)

@router.post("/{source_id}/weights")
async def set_source_weights(source_id: int, weights: List[schemas.SourceWeight], db: AsyncSession = Depends(database.get_db)):
    await crud.set_source_weights(db, source_id, weights)
    return {"status": "ok"}
