import pytest
from app.services.transfer_service import TransferService
from app.models.account import Account
from app.models.user import User

@pytest.mark.asyncio
async def test_transfer_funds_success(session):
    # Setup test data
    user = User(email="test@transfers.com", hashed_password="hashed")
    session.add(user)
    await session.commit()
    await session.refresh(user)

    acc1 = Account(user_id=user.id, account_number="111", currency="USD", balance=50000) # $500.00
    acc2 = Account(user_id=user.id, account_number="222", currency="USD", balance=0)
    session.add_all([acc1, acc2])
    await session.commit()
    await session.refresh(acc1)
    await session.refresh(acc2)

    # Transfer $100.00 (10000 cents)
    await TransferService.transfer_funds(acc1.id, acc2.id, 10000, session)

    # Validate balances
    await session.refresh(acc1)
    await session.refresh(acc2)
    assert acc1.balance == 40000
    assert acc2.balance == 10000

@pytest.mark.asyncio
async def test_transfer_insufficient_funds(session):
    user = User(email="poor@transfers.com", hashed_password="pw")
    session.add(user)
    await session.commit()
    await session.refresh(user)

    acc1 = Account(user_id=user.id, account_number="333", currency="USD", balance=1000)
    acc2 = Account(user_id=user.id, account_number="444", currency="USD", balance=0)
    session.add_all([acc1, acc2])
    await session.commit()

    with pytest.raises(ValueError, match="Insufficient Funds"):
        await TransferService.transfer_funds(acc1.id, acc2.id, 2000, session)

@pytest.mark.asyncio
async def test_transfer_negative_amount(session):
    import uuid
    with pytest.raises(ValueError, match="Transfer amount must be strictly positive"):
        await TransferService.transfer_funds(uuid.uuid4(), uuid.uuid4(), -1000, session)

@pytest.mark.asyncio
async def test_transfer_zero_amount(session):
    import uuid
    with pytest.raises(ValueError, match="Transfer amount must be strictly positive"):
        await TransferService.transfer_funds(uuid.uuid4(), uuid.uuid4(), 0, session)

@pytest.mark.asyncio
async def test_transfer_same_account(session):
    user = User(email="same@transfers.com", hashed_password="pw")
    session.add(user)
    await session.commit()
    await session.refresh(user)

    acc = Account(user_id=user.id, account_number="555", currency="USD", balance=1000)
    session.add(acc)
    await session.commit()

    with pytest.raises(ValueError, match="Cannot transfer to the same account"):
        await TransferService.transfer_funds(acc.id, acc.id, 500, session)
