import pytest
from app.services.account_service import AccountService
from app.models.account import Account
from app.models.user import User

@pytest.mark.asyncio
async def test_get_account_balance(session):
    user = User(email="balance@test.com", hashed_password="pw")
    session.add(user)
    await session.commit()
    await session.refresh(user)

    acc = Account(user_id=user.id, account_number="999", currency="USD", balance=12345)
    session.add(acc)
    await session.commit()

    balance = await AccountService.get_account_balance(session, acc.id)
    assert balance == 12345

@pytest.mark.asyncio
async def test_get_account_not_found(session):
    import uuid
    with pytest.raises(ValueError, match="Account not found"):
        await AccountService.get_account_balance(session, uuid.uuid4())
