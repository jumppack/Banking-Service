from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.account import Account
from app.models.card import Card
from app.schemas.card import CardCreate, CardResponse

router = APIRouter(prefix="/cards", tags=["cards"])

@router.post(
    "/", 
    response_model=CardResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Issue a new physical/virtual card",
    description="Generates a new 16-digit card number, CVC, and Expiry date linked to the specified Account ID. Fails if the user does not own the parent account.",
    response_description="The newly issued Card entity details."
)
async def create_card(
    card_in: CardCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    # Verify account ownership
    result = await session.execute(select(Account).where(Account.id == card_in.account_id))
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        
    if account.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to issue a card for this account")
    
    # Generate random 16 digit card number, 3 digit cvc, and expiry 3 years from now
    import random
    from datetime import datetime
    
    card_number = "".join([str(random.randint(0, 9)) for _ in range(16)])
    cvc = "".join([str(random.randint(0, 9)) for _ in range(3)])
    expiry_year = datetime.now().year + 3
    expiry_month = f"{datetime.now().month:02d}"
    expiry = f"{expiry_month}/{str(expiry_year)[-2:]}"
    
    try:
        new_card = Card(
            account_id=account.id,
            card_number=card_number,
            cvc=cvc,
            expiry=expiry
        )
        
        session.add(new_card)
        await session.commit()
        await session.refresh(new_card)
        
        return new_card
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get(
    "/", 
    response_model=List[CardResponse],
    summary="List my cards",
    description="Fetches all cards linked to any account owned by the currently authenticated user.",
    response_description="A list of Card entities."
)
async def get_cards(
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    # Fetch all cards linked to accounts owned by current_user
    # Using a JOIN equivalent or simply fetching accounts first
    accounts_result = await session.execute(select(Account).where(Account.user_id == current_user.id))
    accounts = accounts_result.scalars().all()
    
    if not accounts:
        return []
        
    account_ids = [acc.id for acc in accounts]
    cards_result = await session.execute(
        select(Card)
        .where(Card.account_id.in_(account_ids))
        .offset(offset)
        .limit(limit)
    )
    
    return cards_result.scalars().all()
