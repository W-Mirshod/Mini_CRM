from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List
from .. import models, schemas, database

router = APIRouter(
    tags=["view"],
)

templates = Jinja2Templates(directory="templates")

@router.get("/leads/", response_model=List[schemas.Lead])
async def read_leads(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.Lead).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/stats/", response_model=schemas.DistributionStats)
async def get_stats(db: AsyncSession = Depends(database.get_db)):
    # Total contacts
    total_res = await db.execute(select(func.count(models.Contact.id)))
    total = total_res.scalar_one()
    
    # By Operator
    op_res = await db.execute(
        select(models.Operator.name, func.count(models.Contact.id))
        .join(models.Operator, models.Contact.operator_id == models.Operator.id)
        .group_by(models.Operator.name)
    )
    by_operator = {name: count for name, count in op_res.all()}
    
    # By Source
    src_res = await db.execute(
        select(models.Source.name, func.count(models.Contact.id))
        .join(models.Source, models.Contact.source_id == models.Source.id)
        .group_by(models.Source.name)
    )
    by_source = {name: count for name, count in src_res.all()}
    
    return {
        "total_contacts": total,
        "by_operator": by_operator,
        "by_source": by_source
    }

@router.get("/documentation/")
async def documentation_page(request: Request):
    return templates.TemplateResponse("docs.html", {"request": request})
