from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class TransactionBase(BaseModel):
    amount: int
    type: str

class TransactionCreate(TransactionBase):
    account_id: UUID
    related_account_id: Optional[UUID] = None

class TransactionResponse(TransactionBase):
    id: UUID
    account_id: UUID
    timestamp: datetime
    related_account_id: Optional[UUID]
    model_config = ConfigDict(from_attributes=True)
