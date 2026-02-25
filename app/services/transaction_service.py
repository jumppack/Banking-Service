from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.models.account import Account
from app.models.transaction import Transaction

class TransactionService:
    @staticmethod
    async def deposit(session: AsyncSession, account_id: UUID, amount: int) -> tuple[Transaction, int]:
        if amount <= 0:
            raise ValueError("Deposit amount must be strictly positive")
            
        try:
            result = await session.execute(select(Account).where(Account.id == account_id))
            account = result.scalar_one_or_none()
            
            if not account:
                raise ValueError("Account not found")
                
            account.balance += amount
            
            tx = Transaction(
                account_id=account_id,
                amount=amount,
                type="deposit",
                related_account_id=None
            )
            
            session.add(tx)
            await session.commit()
            
            # Refresh tx to get auto-generated fields like id and timestamp
            await session.refresh(tx)
            
            return tx, account.balance
            
        except Exception as e:
            await session.rollback()
            raise e

    @staticmethod
    async def withdraw(session: AsyncSession, account_id: UUID, amount: int) -> tuple[Transaction, int]:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be strictly positive")
            
        try:
            result = await session.execute(select(Account).where(Account.id == account_id))
            account = result.scalar_one_or_none()
            
            if not account:
                raise ValueError("Account not found")
                
            if account.balance < amount:
                raise ValueError("Insufficient Funds")
                
            account.balance -= amount
            
            tx = Transaction(
                account_id=account_id,
                amount=-amount,
                type="withdrawal",
                related_account_id=None
            )
            
            session.add(tx)
            await session.commit()
            
            # Refresh tx to get auto-generated fields
            await session.refresh(tx)
            
            return tx, account.balance
            
        except Exception as e:
            await session.rollback()
            raise e
