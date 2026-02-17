/**
 * API client service for Home Banking backend.
 * Provides typed methods for all backend endpoints.
 */

import type {
  Account,
  Transaction,
  TransferRequest,
  TransferResponse,
  TransferErrorResponse,
} from "../types/api";

/**
 * Base URL for API requests.
 * Uses VITE_API_BASE_URL environment variable or defaults to '/api'.
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

/**
 * Generic error class for API errors.
 */
export class ApiError extends Error {
  status: number;
  response?: unknown;

  constructor(message: string, status: number, response?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.response = response;
  }
}

/**
 * Helper function to handle API responses and errors.
 * @param response - Fetch Response object
 * @returns Parsed JSON response
 * @throws ApiError for non-2xx responses
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
    let errorResponse: unknown;

    try {
      errorResponse = await response.json();
      if (typeof errorResponse === "object" && errorResponse !== null) {
        if ("error" in errorResponse) {
          errorMessage = (errorResponse as TransferErrorResponse).error;
        } else if ("title" in errorResponse) {
          errorMessage = (errorResponse as { title: string }).title;
        }
      }
    } catch {
      // If JSON parsing fails, use the default error message
    }

    throw new ApiError(errorMessage, response.status, errorResponse);
  }

  return response.json() as Promise<T>;
}

/**
 * Fetches all accounts from the backend.
 * @returns Promise resolving to array of Account objects
 * @throws ApiError if the request fails
 */
export async function getAccounts(): Promise<Account[]> {
  const response = await fetch(`${API_BASE_URL}/accounts`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  return handleResponse<Account[]>(response);
}

/**
 * Fetches transactions with optional filtering.
 * @param accountId - Optional account ID to filter transactions
 * @param limit - Maximum number of transactions to return
 * @param offset - Number of transactions to skip for pagination
 * @returns Promise resolving to array of Transaction objects
 * @throws ApiError if the request fails
 */
export async function getTransactions(
  accountId?: string,
  limit?: number,
  offset?: number
): Promise<Transaction[]> {
  const params = new URLSearchParams();

  if (accountId) {
    params.append("accountId", accountId);
  }
  if (limit !== undefined) {
    params.append("limit", limit.toString());
  }
  if (offset !== undefined) {
    params.append("offset", offset.toString());
  }

  const queryString = params.toString();
  const url = `${API_BASE_URL}/transactions${queryString ? `?${queryString}` : ""}`;

  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  return handleResponse<Transaction[]>(response);
}

/**
 * Creates a transfer between two accounts.
 * @param request - Transfer request containing source, destination, amount, and description
 * @returns Promise resolving to TransferResponse with transaction IDs and timestamp
 * @throws ApiError if the request fails or validation errors occur
 */
export async function createTransfer(
  request: TransferRequest
): Promise<TransferResponse> {
  const response = await fetch(`${API_BASE_URL}/transfers`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  return handleResponse<TransferResponse>(response);
}
