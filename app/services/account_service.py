from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import uuid
from app.models.account import Account
from app.models.transaction import Transaction

class AccountService:
    @staticmethod
    def _generate_account_number() -> str:
        # Generate a 12-character alphanumeric account number
        return str(uuid.uuid4()).replace("-", "")[:12].upper()

    @staticmethod
    async def create_account(session: AsyncSession, user_id: UUID, currency: str = "USD") -> Account:
        import sqlalchemy.exc
        
        max_attempts = 5
        for attempt in range(max_attempts):
            account_number = AccountService._generate_account_number()
            
            new_account = Account(
                user_id=user_id,
                account_number=account_number,
                currency=currency,
                balance=0
            )
            
            session.add(new_account)
            
            try:
                await session.commit()
                await session.refresh(new_account)
                return new_account
            except sqlalchemy.exc.IntegrityError as e:
                await session.rollback()
                # Check if it's specifically an account_number collision
                # SQLite returns 'UNIQUE constraint failed: accounts.account_number'
                if "account_number" in str(e):
                    continue
                # If it's a different IntegrityError (e.g., user doesn't exist), re-raise
                raise e
            except Exception as e:
                await session.rollback()
                raise e
                
        # If we exhausted all attempts, raise a clear error
        raise RuntimeError("Failed to generate a unique account number after multiple attempts.")
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
    async def get_transactions(session: AsyncSession, account_id: UUID, limit: int = 100, offset: int = 0):
        result = await session.execute(
            select(Transaction)
            .where(Transaction.account_id == account_id)
            .order_by(Transaction.timestamp.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()
