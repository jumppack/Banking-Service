
# Future Considerations & Architectural Evolution

This document outlines the anticipated architectural bottlenecks and proposed system evolutions required to transition this banking service from a local, monolithic MVP to a highly available, globally distributed financial platform.

---

### 1. Multi-Currency & Cryptocurrency Scaling

**Current State:** To prevent floating-point precision errors inherent to SQLite and Python `float` types, the current architecture stores all fiat currency (e.g., USD) as `Integer` types representing the smallest fractional unit (cents).

**Future Considerations:**
As the platform scales to support cryptocurrencies (which require significantly higher precision, such as Bitcoin's 8 decimal places or Ethereum's 18 decimal places), the data layer will need to evolve.

* **Storage Pattern:** We will maintain the "smallest indivisible unit" pattern (e.g., Bitcoin stored as Satoshis, Ethereum as Wei).
* **Database Migration:** The database will be migrated from SQLite to a robust relational database like PostgreSQL.
* **Type Casting:** We will transition currency columns to PostgreSQL's arbitrary precision `NUMERIC(precision, scale)` types (e.g., `NUMERIC(36, 18)` for EVM-compatible chains) to guarantee mathematical exactness without overflowing integer limits.

---

### 2. Event-Driven Architecture & High-Throughput Processing

**Current State:** Money transfers and account updates are handled synchronously within the FastAPI request lifecycle. While functional for low traffic, this couples the API response time directly to database write speeds and external system latency.

**Future Considerations:**
To handle thousands of transactions per second (TPS), the system will pivot to a cloud-native, event-driven architecture.

* **Message Brokers:** Implementing Apache Kafka or RabbitMQ to decouple the API layer from the transaction processing engine.
* **Asynchronous Workers:** The API will instantly return a "Transfer Initiated" status (HTTP 202), while background worker nodes process the complex ledger updates, balance checks, and anti-fraud verifications from the queue.
* **Dead Letter Queues (DLQ):** Implementing DLQs to safely capture and manually review failed transaction events without dropping financial data.
* **Distributed Tracing:** Implementing OpenTelemetry and Jaeger to inject trace IDs into every request. This ensures that as a transaction moves from the API, into Kafka, and through the worker nodes, we have a complete, visual timeline of the event for rapid debugging.

---

### 3. AI-Enhanced Security & AI companion in the app

**Current State:** Transaction validation relies on deterministic, rule-based logic (e.g., sufficient balance checks) handled entirely by standard Python services.

**Future Considerations:**
Integrating advanced AI system design to elevate both platform security and user experience.

* **Real-Time Fraud Detection:** Deploying machine learning models to analyze transaction velocity, location anomalies, and behavioral patterns in real-time, temporarily freezing suspicious transfers.
* **Intelligent Transaction Categorization:** Utilizing LLM APIs to automatically enrich and categorize raw vendor strings into clean user-facing categories (e.g., turning "POS DEBIT 1234 SQ *COFFEE" into "Food & Dining").
* **Conversational AI Chatbot:** Integrating a secure, LLM-powered chatbot directly into the frontend interface. By utilizing a Retrieval-Augmented Generation (RAG) architecture, this assistant will be securely isolated to query only the active user's transaction history, allowing users to ask complex natural language questions (e.g., "How much did I spend on groceries last month compared to this month?") without exposing PII to public models.

---

### 4. Cloud-Native Deployment & Orchestration

**Current State:** The application is containerized using Docker and orchestrated locally via `docker-compose.yml` with a local SQLite file.

**Future Considerations:**
Moving to a highly available, fault-tolerant infrastructure.

* **Kubernetes (K8s):** Transitioning deployment to a managed Kubernetes cluster (e.g., EKS or GKE) for automated scaling, self-healing, and zero-downtime rolling updates.
* **Distributed Databases:** Replacing the local database with a globally distributed, highly available database cluster (like Amazon Aurora or CockroachDB) to ensure multi-region redundancy and low-latency read replicas for user statements.

---

### 5. Advanced Security & Compliance

**Current State:** The system utilizes standard JWT-based authentication and secure password hashing via bcrypt.

**Future Considerations:**
Banking platforms require military-grade security and strict regulatory compliance.

* **Identity Provider Integration:** Migrating from custom user management to an enterprise Identity and Access Management (IAM) provider using OAuth2 and OpenID Connect (OIDC).
* **Key Management System (KMS):** Utilizing AWS
