from pydantic import BaseModel
from uuid import UUID

class TransferCreate(BaseModel):
    from_account_id: UUID
    to_identifier: str
    amount: int
