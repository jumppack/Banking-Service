from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.models.account import Account
from app.models.transaction import Transaction

class AccountService:
    @staticmethod
    async def get_account(session: AsyncSession, account_id: UUID):
        result = await session.execute(select(Account).where(Account.id == account_id))
        return result.scalar_one_or_none()
        
    @staticmethod
    async def get_account_balance(session: AsyncSession, account_id: UUID):
        account = await AccountService.get_account(session, account_id)
        if not account:
            raise ValueError("Account not found")
        return account.balance
        
    @staticmethod
    async def get_transactions(session: AsyncSession, account_id: UUID):
        result = await session.execute(select(Transaction).where(Transaction.account_id == account_id))
        return result.scalars().all()
