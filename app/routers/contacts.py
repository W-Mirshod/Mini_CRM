from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .. import crud, schemas, database, logic

router = APIRouter(
    prefix="/contacts",
    tags=["contacts"],
)

@router.post("/", response_model=schemas.Contact)
async def create_contact(contact: schemas.ContactCreate, db: AsyncSession = Depends(database.get_db)):
    # 1. Find or create lead
    lead = await crud.get_lead_by_identifier(db, contact.lead_identifier)
    if not lead:
        lead = await crud.create_lead(db, contact.lead_identifier)
    
    # 2. Select operator
    operator_id = await logic.select_operator(db, contact.source_id)
    
    # 3. Create contact
    # Note: If operator_id is None, we still create the contact but it's unassigned.
    # The prompt says: "If no eligible operators exist: either create contact without an operator or return 4xx error"
    # We choose to create it without an operator so we don't lose the lead.
    new_contact = await crud.create_contact(db, lead.id, contact.source_id, operator_id)
    
    return new_contact
