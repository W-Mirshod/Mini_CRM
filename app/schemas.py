from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class OperatorBase(BaseModel):
    name: str
    is_active: bool = True
    workload_limit: int = 10

class OperatorCreate(OperatorBase):
    pass

class Operator(OperatorBase):
    id: int

    class Config:
        from_attributes = True

class SourceBase(BaseModel):
    name: str

class SourceCreate(SourceBase):
    pass

class Source(SourceBase):
    id: int

    class Config:
        from_attributes = True

class SourceWeight(BaseModel):
    operator_id: int
    weight: int

class LeadBase(BaseModel):
    identifier: str

class LeadCreate(LeadBase):
    pass

class Lead(LeadBase):
    id: int

    class Config:
        from_attributes = True

class ContactCreate(BaseModel):
    lead_identifier: str
    source_id: int

class Contact(BaseModel):
    id: int
    lead_id: int
    source_id: int
    operator_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class DistributionStats(BaseModel):
    total_contacts: int
    by_operator: dict[str, int]
    by_source: dict[str, int]
