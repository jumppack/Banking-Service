from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.schemas.common import PositiveAmountMixin

class TransactionBase(BaseModel):
    amount: int = Field(..., description="The transaction amount in cents. Positive indicates a credit, negative indicates a debit.")
    type: str = Field(..., description="The category of transaction (e.g., 'DEPOSIT', 'WITHDRAWAL', 'TRANSFER_IN', 'TRANSFER_OUT').")

class TransactionCreate(TransactionBase):
    account_id: UUID = Field(..., description="The primary account executing the transaction.")
    related_account_id: Optional[UUID] = Field(default=None, description="The counterparty account ID, if this is part of an internal transfer.")

class TransactionResponse(TransactionBase):
    id: UUID = Field(..., description="The internal UUID of the transaction record.")
    account_id: UUID = Field(..., description="The primary account executing the transaction.")
    timestamp: datetime = Field(..., description="The exact UTC timestamp the transaction was recorded onto the ledger.")
    related_account_id: Optional[UUID] = Field(default=None, description="The counterparty account ID, if this is part of an internal transfer.")
    counterparty_name: Optional[str] = Field(default=None, description="The resolved human-readable name of the counterparty, if applicable.")
    model_config = ConfigDict(from_attributes=True)

class TransactionAmountRequest(PositiveAmountMixin):
    pass

class TransactionPostResponse(BaseModel):
    transaction: TransactionResponse = Field(..., description="The executed transaction record.")
    balance: int = Field(..., description="The updated account balance in cents.")
