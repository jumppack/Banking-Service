from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class TransactionBase(BaseModel):
    amount: int
    type: str

class TransactionCreate(TransactionBase):
    account_id: UUID
    related_account_id: UUID | None = None

class TransactionResponse(TransactionBase):
    id: UUID
    account_id: UUID
    timestamp: datetime
    related_account_id: UUID | None
    model_config = ConfigDict(from_attributes=True)
