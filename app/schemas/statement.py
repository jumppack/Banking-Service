from pydantic import BaseModel
from typing import List
from uuid import UUID

from app.schemas.transaction import TransactionResponse

class StatementResponse(BaseModel):
    account_id: UUID
    account_number: str
    currency: str
    starting_balance: int # for simplicity, we mock starting_balance as 0 or current balance - net changes
    ending_balance: int
    total_credits: int
    total_debits: int
    transaction_count: int
    transactions: List[TransactionResponse]
