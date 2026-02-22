from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.schemas.statement import StatementResponse
from app.schemas.transaction import TransactionResponse

router = APIRouter(prefix="/accounts/{account_id}/statement", tags=["statements"])

@router.get("/", response_model=StatementResponse)
async def get_statement(
    account_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    # Verify account ownership
    result = await session.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        
    if account.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view statement for this account")
        
    # Fetch transactions for statement mock
    tx_result = await session.execute(select(Transaction).where(Transaction.account_id == account_id).order_by(Transaction.timestamp.desc()))
    transactions = tx_result.scalars().all()
    
    total_credits = sum(tx.amount for tx in transactions if tx.type == "credit")
    total_debits = sum(tx.amount for tx in transactions if tx.type == "debit")
    net_change = total_credits - total_debits
    starting_balance = account.balance - net_change
    
    return StatementResponse(
        account_id=account.id,
        account_number=account.account_number,
        currency=account.currency,
        starting_balance=starting_balance,
        ending_balance=account.balance,
        total_credits=total_credits,
        total_debits=total_debits,
        transaction_count=len(transactions),
        transactions=[TransactionResponse.model_validate(tx) for tx in transactions]
    )
