### Future Consideration: Multi-Currency & Cryptocurrency Scaling

**Current State:** To prevent floating-point precision errors inherent to SQLite and Python `float` types, the current architecture stores all fiat currency (e.g., USD) as `Integer` types representing the smallest fractional unit (cents).

**Future Roadmap (Cryptocurrency Integration):**
As the platform scales to support cryptocurrencies (which require significantly higher precision, such as Bitcoin's 8 decimal places or Ethereum's 18 decimal places), the data layer will need to evolve.

1. **Storage Pattern:** We will maintain the "smallest indivisible unit" pattern. Bitcoin will be stored as Satoshis, and Ethereum as Wei.
2. **Database Migration:** The database will be migrated from SQLite to PostgreSQL.
3. **Type Casting:** We will transition the currency columns from standard `Integer` to PostgreSQL's arbitrary precision `NUMERIC(precision, scale)` types (e.g., `NUMERIC(36, 18)` for EVM-compatible chains). This ensures mathematical exactness for fractional token transfers without overflowing 64-bit integer limits.
