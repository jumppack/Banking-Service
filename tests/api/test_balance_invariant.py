import pytest
import sqlalchemy.exc

@pytest.mark.asyncio
async def test_balance_invariant_constraint(session):
    from app.models.account import Account
    import uuid
    
    # Create test account directly using DB session
    acc = Account(
        user_id=uuid.uuid4(),
        account_number=str(uuid.uuid4().hex)[:12],
        currency="USD",
        balance=-1  # Violates constraint
    )
    
    session.add(acc)
    
    with pytest.raises(sqlalchemy.exc.IntegrityError) as exc_info:
        await session.commit()
        
    assert "ck_accounts_balance_nonnegative" in str(exc_info.value)
