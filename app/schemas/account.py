from pydantic import BaseModel, ConfigDict
from uuid import UUID

class AccountBase(BaseModel):
    currency: str = "USD"

class AccountCreate(AccountBase):
    user_id: UUID
    account_number: str

class AccountResponse(AccountBase):
    id: UUID
    user_id: UUID
    account_number: str
    balance: int
    model_config = ConfigDict(from_attributes=True)
