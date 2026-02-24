from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.models.account import Account
from app.models.transaction import Transaction

class TransferService:
    @staticmethod
    async def transfer_funds(from_account_id: UUID, to_account_id: UUID, amount: int, session: AsyncSession):
        """
        Executes a money transfer atomically.
        """
        # Basic Validation
        if amount <= 0:
            raise ValueError("Transfer amount must be strictly positive")
        if from_account_id == to_account_id:
            raise ValueError("Cannot transfer to the same account")

        try:
            # Fetch both accounts without FOR UPDATE (SQLite doesn't support row-level locking)
            from_account_result = await session.execute(select(Account).where(Account.id == from_account_id))
            from_account = from_account_result.scalar_one_or_none()
            
            to_account_result = await session.execute(select(Account).where(Account.id == to_account_id))
            to_account = to_account_result.scalar_one_or_none()
            
            # Validate existence
            if not from_account or not to_account:
                raise ValueError("Account not found")
            
            # Check sufficient balance
            if from_account.balance < amount:
                raise ValueError("Insufficient Funds")
                
            # Update account balances
            from_account.balance -= amount
            to_account.balance += amount
            
            # Create offsetting Transaction records
            # Debit transaction for sender
            debit_tx = Transaction(
                account_id=from_account_id,
                amount=-amount,
                type="transfer_out",
                related_account_id=to_account_id
            )
            
            # Credit transaction for receiver
            credit_tx = Transaction(
                account_id=to_account_id,
                amount=amount,
                type="credit",
                related_account_id=from_account_id
            )
            
            session.add_all([debit_tx, credit_tx])
            
            # Explicitly commit the transaction block
            await session.commit()
            
            return True
            
        except Exception as e:
            # Rollback in case of any failure ensuring atomicity
            await session.rollback()
            raise e
