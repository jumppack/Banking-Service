from pydantic import BaseModel, Field

class PositiveAmountMixin(BaseModel):
    amount: int = Field(..., gt=0, description="The amount in cents. Must be strictly positive.")
