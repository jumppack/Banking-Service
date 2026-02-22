from pydantic import BaseModel, ConfigDict
from uuid import UUID

class CardBase(BaseModel):
    pass # we can add preferences like card limit later if needed

class CardCreate(CardBase):
    account_id: UUID

class CardResponse(CardBase):
    id: UUID
    account_id: UUID
    card_number: str
    cvc: str
    expiry: str
    
    model_config = ConfigDict(from_attributes=True)
