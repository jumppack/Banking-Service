import pytest
from app.services.account_service import AccountService
from app.models.account import Account
from app.models.user import User

@pytest.mark.asyncio
async def test_get_account_balance(session):
    user = User(email="balance@test.com", hashed_password="securepw")
    session.add(user)
    await session.commit()
    await session.refresh(user)

    acc = Account(user_id=user.id, account_number="999", currency="USD", balance=12345)
    session.add(acc)
    await session.commit()

    balance = await AccountService.get_account_balance(session, acc.id)
    assert balance == 12345

@pytest.mark.asyncio
async def test_get_account_success(session):
    user = User(email="getacc@test.com", hashed_password="securepw")
    session.add(user)
    await session.commit()
    await session.refresh(user)

    acc = Account(user_id=user.id, account_number="888", currency="USD", balance=100)
    session.add(acc)
    await session.commit()
    await session.refresh(acc)

    fetched_acc = await AccountService.get_account(session, acc.id)
    assert fetched_acc.account_number == "888"

@pytest.mark.asyncio
async def test_get_transactions_pagination(session):
    from app.models.transaction import Transaction
    user = User(email="tx@test.com", hashed_password="securepw")
    session.add(user)
    await session.commit()
    await session.refresh(user)

    acc = Account(user_id=user.id, account_number="777", currency="USD", balance=100)
    session.add(acc)
    await session.commit()
    await session.refresh(acc)

    for i in range(5):
        tx = Transaction(account_id=acc.id, amount=10, type="deposit")
        session.add(tx)
    await session.commit()

    txs = await AccountService.get_transactions(session, acc.id, limit=2, offset=0)
    assert len(txs) == 2

@pytest.mark.asyncio
async def test_get_account_not_found(session):
    import uuid
    with pytest.raises(ValueError, match="Account not found"):
        await AccountService.get_account_balance(session, uuid.uuid4())
