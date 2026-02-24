import asyncio
import uuid
import sys
import random
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.card import Card
from app.core.security import get_password_hash

# Configure Database Connection
DATABASE_URL = "sqlite+aiosqlite:///./data/banking.db"
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

def generate_card():
    card_number = "".join([str(random.randint(0, 9)) for _ in range(16)])
    cvc = "".join([str(random.randint(0, 9)) for _ in range(3)])
    expiry_year = datetime.now().year + 3
    expiry_month = f"{datetime.now().month:02d}"
    expiry = f"{expiry_month}/{str(expiry_year)[-2:]}"
    return card_number, cvc, expiry

async def seed_database():
    print("Connecting to database...")
    async with SessionLocal() as session:
        print("WARNING: Wiping existing database records...")
        await session.execute(text("DELETE FROM cards"))
        await session.execute(text("DELETE FROM transactions"))
        await session.execute(text("DELETE FROM accounts"))
        await session.execute(text("DELETE FROM users"))
        await session.commit()
        print("Database wiped successfully.")

        print("Seeding 5 Complex Users...")
        users = []
        names = ["karan", "lava", "alice", "bob", "charlie"]
        for name in names:
            user = User(
                id=uuid.uuid4(),
                email=f"{name}@example.com",
                hashed_password=get_password_hash("securepassword123"),
                is_active=True
            )
            users.append(user)
        session.add_all(users)
        await session.flush()

        print("Seeding Accounts (Checking & Savings)...")
        accounts = []
        for user in users:
            # Everyone gets a checking account with $10,000 to $50,000
            checking = Account(
                id=uuid.uuid4(),
                user_id=user.id,
                account_number=f"100{random.randint(1000000, 9999999)}",
                currency="USD",
                balance=random.randint(1000000, 5000000) 
            )
            accounts.append(checking)
            
            # Everyone gets a savings account with $5,000 to $20,000
            savings = Account(
                id=uuid.uuid4(),
                user_id=user.id,
                account_number=f"200{random.randint(1000000, 9999999)}",
                currency="USD",
                balance=random.randint(500000, 2000000)
            )
            accounts.append(savings)
        session.add_all(accounts)
        await session.flush()

        print("Seeding Complex Transaction Matrix...")
        transactions = []
        # Generate 20 random cross-account transfers
        for _ in range(20):
            sender_acc = random.choice(accounts)
            receiver_acc = random.choice([a for a in accounts if a.id != sender_acc.id])
            transfer_amount = random.randint(1000, 50000) # $10.00 to $500.00

            tx_out = Transaction(account_id=sender_acc.id, related_account_id=receiver_acc.id, amount=transfer_amount, type="transfer_out")
            tx_in = Transaction(account_id=receiver_acc.id, related_account_id=sender_acc.id, amount=transfer_amount, type="transfer_in")
            transactions.extend([tx_out, tx_in])
        session.add_all(transactions)
        await session.flush()

        print("Seeding Dynamically Generated Debit Cards...")
        cards = []
        for account in accounts:
            # We will attach a debit card to every CHECKING account (which start with '100')
            if account.account_number.startswith("100"):
                c_num, cvc, exp = generate_card()
                card = Card(
                    id=uuid.uuid4(),
                    account_id=account.id,
                    card_number=c_num,
                    cvc=cvc,
                    expiry=exp
                )
                cards.append(card)
                
                # Randomly give half of the checking accounts a SECOND supplementary card
                if random.choice([True, False]):
                    c_num2, cvc2, exp2 = generate_card()
                    card2 = Card(
                        id=uuid.uuid4(),
                        account_id=account.id,
                        card_number=c_num2,
                        cvc=cvc2,
                        expiry=exp2
                    )
                    cards.append(card2)
        session.add_all(cards)

        await session.commit()
        print(f"✅ Database successfully seeded with {len(users)} Users, {len(accounts)} Accounts, {len(transactions)//2} distinct Transfers, and {len(cards)} Cards.")

    await engine.dispose()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_database())
