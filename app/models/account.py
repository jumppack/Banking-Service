import uuid
from sqlalchemy import ForeignKey
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    account_number: Mapped[str] = mapped_column(unique=True, index=True)
    balance: Mapped[int] = mapped_column(default=0)
    currency: Mapped[str] = mapped_column(default="USD")

    __table_args__ = (
        sa.CheckConstraint("balance >= 0", name="ck_accounts_balance_nonnegative"),
    )
