from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID

class AccountBase(BaseModel):
    currency: str = Field(default="USD", description="The 3-letter currency code for the account.", min_length=3, max_length=3)

class AccountCreate(AccountBase):
    user_id: UUID = Field(..., description="The UUID of the user who owns this account.")
    account_number: str = Field(..., description="The globally unique 10-digit account number.")

class AccountResponse(AccountBase):
    id: UUID = Field(..., description="The internal UUID of the account record.")
    user_id: UUID = Field(..., description="The UUID of the user who owns this account.")
    account_number: str = Field(..., description="The globally unique 10-digit account number.")
    balance: int = Field(..., description="The current ledger balance of the account in cents (e.g., 1000 = $10.00).")
    model_config = ConfigDict(from_attributes=True)
