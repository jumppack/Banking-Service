from pydantic import BaseModel
from uuid import UUID
from app.schemas.common import PositiveAmountMixin

class TransferCreate(PositiveAmountMixin):
    from_account_id: UUID
    to_identifier: str
