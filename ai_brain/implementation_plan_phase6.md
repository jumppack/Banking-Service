# Phase 6 Implementation Plan: Frontend UI Integration

This plan outlines the architecture and execution strategy for building the consumer-facing customer dashboard using React and Vite.

## 1. Scaffolding & Dependencies
- **Build Tool:** Vite (React Template)
- **Networking:** Axios
- **Routing:** React-Router-DOM
- **Styling:** Tailwind CSS (with PostCSS & Autoprefixer)
- **Icons:** Lucide-React

## 2. Directory Structure & Component Architecture
The application will adhere to a strict modular component tree to maintain scalability and clean integration with the FastAPI backend:

```text
frontend/
├── src/
│   ├── api/
│   │   └── axios.js                // Configures BaseURL (http://localhost:8000) & JWT interceptors
│   ├── context/
│   │   └── AuthContext.jsx         // Manages login state, parses JWT payload, and clears localStorage on logout
│   ├── components/                 // Reusable UI/logic pieces
│   │   ├── ProtectedRoute.jsx      // Wrapper ensuring only authenticated users can access the Dashboard
│   │   ├── Navigation.jsx          // Top bar with "Logout" and user context
│   │   ├── TransferForm.jsx        // Form validating destination account and transfer amounts
│   │   ├── TransactionHistory.jsx  // Renders the paginated ledger in a clean table format
│   │   └── CardDisplay.jsx         // Visual representation of the dynamically seeded Debit Card
│   ├── pages/                      // High-level route views
│   │   ├── Login.jsx               // OAuth2 Password Bearer form handling authentication
│   │   └── Dashboard.jsx           // Grid layout aggregating Account Balances, Cards, and Forms
│   ├── App.jsx                     // React-Router-Dom configuration binding paths to Pages
│   └── main.jsx                    // Entry point injecting AuthContext into the React DOM
```

## 3. Workflow Strategy
1. **Authentication Backbone (`AuthContext.jsx` & `axios.js`):** Instantly captures the `access_token` returned from the FastAPI `/auth/login` endpoint and automatically attaches `Authorization: Bearer <token>` to every subsequent intercepted API call.
2. **Dashboard Controller (`Dashboard.jsx`):** Once authenticated, the Dashboard orchestrates parallel API requests retrieving Account balances, generated Cards, and historical Transactions, cascading the state down to presentational components via props.
3. **Action Execution (`TransferForm.jsx`):** Dispatches secure state-mutating requests back to the API and updates the UI optimisticially or upon successful refetch.
