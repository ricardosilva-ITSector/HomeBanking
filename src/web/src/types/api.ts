/**
 * TypeScript interfaces matching the backend API models.
 * Backend uses camelCase JSON serialization.
 */

/**
 * Account type enum matching backend AccountType.
 */
export type AccountType = "Checking" | "Savings";

/**
 * Transaction type enum matching backend TransactionType.
 */
export type TransactionType = "Debit" | "Credit";

/**
 * Bank account model matching backend Account entity.
 */
export interface Account {
  id: string;
  accountNumber: string;
  accountName: string;
  type: AccountType;
  balance: number;
  currency: string;
  createdAt: string;
}

/**
 * Transaction model matching backend Transaction entity.
 */
export interface Transaction {
  id: string;
  accountId: string;
  date: string;
  description: string;
  amount: number;
  type: TransactionType;
  category: string;
  balanceAfter: number;
}

/**
 * Paginated response DTO for transaction queries.
 */
export interface PaginatedTransactionsResponse {
  totalCount: number;
  transactions: Transaction[];
}

/**
 * Request DTO for creating a transfer between accounts.
 */
export interface TransferRequest {
  fromAccountId: string;
  toAccountId: string;
  amount: number;
  description?: string;
}

/**
 * Response DTO for a successful transfer operation.
 */
export interface TransferResponse {
  debitTransactionId: string;
  creditTransactionId: string;
  timestamp: string;
}

/**
 * Error response DTO for transfer validation errors.
 */
export interface TransferErrorResponse {
  error: string;
}
