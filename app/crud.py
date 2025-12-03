from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from . import models, schemas

async def create_operator(db: AsyncSession, operator: schemas.OperatorCreate):
    db_operator = models.Operator(**operator.dict())
    db.add(db_operator)
    await db.commit()
    await db.refresh(db_operator)
    return db_operator

async def get_operators(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Operator).offset(skip).limit(limit))
    return result.scalars().all()

async def get_operator(db: AsyncSession, operator_id: int):
    result = await db.execute(select(models.Operator).where(models.Operator.id == operator_id))
    return result.scalar_one_or_none()

async def update_operator(db: AsyncSession, operator_id: int, is_active: bool, workload_limit: int):
    db_operator = await get_operator(db, operator_id)
    if db_operator:
        db_operator.is_active = is_active
        db_operator.workload_limit = workload_limit
        await db.commit()
        await db.refresh(db_operator)
    return db_operator

async def create_source(db: AsyncSession, source: schemas.SourceCreate):
    db_source = models.Source(name=source.name)
    db.add(db_source)
    await db.commit()
    await db.refresh(db_source)
    return db_source

async def set_source_weights(db: AsyncSession, source_id: int, weights: list[schemas.SourceWeight]):
    # Clear existing weights for this source
    await db.execute(models.SourceOperatorConfig.__table__.delete().where(models.SourceOperatorConfig.source_id == source_id))
    
    for w in weights:
        db_config = models.SourceOperatorConfig(source_id=source_id, operator_id=w.operator_id, weight=w.weight)
        db.add(db_config)
    
    await db.commit()
    return True

async def get_lead_by_identifier(db: AsyncSession, identifier: str):
    result = await db.execute(select(models.Lead).where(models.Lead.identifier == identifier))
    return result.scalar_one_or_none()

async def create_lead(db: AsyncSession, identifier: str):
    db_lead = models.Lead(identifier=identifier)
    db.add(db_lead)
    await db.commit()
    await db.refresh(db_lead)
    return db_lead

async def create_contact(db: AsyncSession, lead_id: int, source_id: int, operator_id: int | None):
    db_contact = models.Contact(lead_id=lead_id, source_id=source_id, operator_id=operator_id)
    db.add(db_contact)
    await db.commit()
    await db.refresh(db_contact)
    return db_contact

async def get_operator_workload(db: AsyncSession, operator_id: int):
    # Count contacts for this operator. 
    # NOTE: "Active" definition is up to us. For simplicity, let's count ALL contacts for now 
    # or maybe contacts in the last X days? 
    # The prompt says "define 'active' as you see fit". 
    # Let's assume all contacts are "active" for now to keep it simple, 
    # or we could add a "status" field later.
    # A better approach for a CRM is usually "open" status. 
    # But given the schema constraints, let's just count all contacts assigned to this operator.
    # To make it realistic, let's say "active" means created in the last 24 hours? 
    # Or just total count? Let's go with total count for simplicity of the "limit" logic demonstration.
    result = await db.execute(select(func.count(models.Contact.id)).where(models.Contact.operator_id == operator_id))
    return result.scalar_one()
