from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.account import Account
from app.schemas.transaction import TransactionResponse, TransactionAmountRequest, TransactionPostResponse
from app.services.account_service import AccountService
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/accounts/{account_id}/transactions", tags=["transactions"])

@router.get(
    "/", 
    response_model=List[TransactionResponse],
    summary="List account transactions",
    description="Fetches a paginated ledger sequence of transactions (credits/debits) associated with the specified account.",
    response_description="A list of executed transactions. If internal transfers occurred, counterparty resolution is attempted."
)
async def get_transactions(
    account_id: uuid.UUID,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    # Verify account ownership first
    result = await session.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        
    if account.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view transactions for this account")
        
    try:
        transactions = await AccountService.get_transactions(session, account_id, limit, offset)
        
        response_data = []
        for tx in transactions:
            counterparty = None
            if tx.related_account_id:
                # Resolve the linked Account and then the User to get the email
                acc_result = await session.execute(select(Account).where(Account.id == tx.related_account_id))
                related_acc = acc_result.scalar_one_or_none()
                if related_acc:
                    user_result = await session.execute(select(User).where(User.id == related_acc.user_id))
                    related_user = user_result.scalar_one_or_none()
                    if related_user:
                        counterparty = related_user.email
            
            tx_dict = TransactionResponse.model_validate(tx).model_dump()
            tx_dict["counterparty_name"] = counterparty
            response_data.append(tx_dict)
            
        return response_data
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post(
    "/deposit",
    response_model=TransactionPostResponse,
    summary="Deposit funds into account",
    description="Adds funds to the specified account. The account must belong to the authenticated user.",
    response_description="The resulting transaction and the updated balance."
)
async def deposit(
    account_id: uuid.UUID,
    request: TransactionAmountRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    result = await session.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        
    if account.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to deposit into this account")
        
    try:
        tx, balance = await TransactionService.deposit(session, account_id, request.amount)
        return {"transaction": tx, "balance": balance}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post(
    "/withdraw",
    response_model=TransactionPostResponse,
    summary="Withdraw funds from account",
    description="Withdraws funds from the specified account. The account must belong to the authenticated user and have sufficient balance.",
    response_description="The resulting transaction and the updated balance."
)
async def withdraw(
    account_id: uuid.UUID,
    request: TransactionAmountRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    result = await session.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        
    if account.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to withdraw from this account")
        
    try:
        tx, balance = await TransactionService.withdraw(session, account_id, request.amount)
        return {"transaction": tx, "balance": balance}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
