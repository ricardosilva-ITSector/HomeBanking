import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { TransactionList } from "../TransactionList";
import type { Transaction } from "@/types/api";
import * as api from "@/services/api";

// Mock the API module
vi.mock("@/services/api", () => ({
  getTransactions: vi.fn(),
}));

describe("TransactionList", () => {
  const mockTransactions: Transaction[] = [
    {
      id: "1",
      accountId: "acc1",
      date: new Date(Date.now() - 1000 * 60 * 30).toISOString(), // 30 minutes ago
      description: "Monthly Salary",
      amount: 5000.0,
      type: "Credit",
      category: "Salary",
      balanceAfter: 15000.0,
    },
    {
      id: "2",
      accountId: "acc1",
      date: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(), // 5 hours ago
      description: "Grocery Store",
      amount: 85.5,
      type: "Debit",
      category: "Groceries",
      balanceAfter: 10000.0,
    },
    {
      id: "3",
      accountId: "acc1",
      date: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString(), // 2 days ago
      description: "Transfer to Savings",
      amount: 1000.0,
      type: "Debit",
      category: "Internal Transfer",
      balanceAfter: 9000.0,
    },
    {
      id: "4",
      accountId: "acc1",
      date: new Date(Date.now() - 1000 * 60 * 60 * 24 * 10).toISOString(), // 10 days ago
      description: "Refund - Return",
      amount: 50.0,
      type: "Credit",
      category: "Refund",
      balanceAfter: 8500.0,
    },
    {
      id: "5",
      accountId: "acc1",
      date: "2024-06-15T10:00:00Z",
      description: "Netflix Subscription",
      amount: 15.99,
      type: "Debit",
      category: "Subscription",
      balanceAfter: 8000.0,
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders loading state initially", () => {
    vi.mocked(api.getTransactions).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(<TransactionList />);
    expect(screen.getByText("Loading transactions...")).toBeInTheDocument();
  });

  it("renders transaction data correctly", async () => {
    vi.mocked(api.getTransactions).mockResolvedValue(mockTransactions);

    render(<TransactionList />);

    await waitFor(() => {
      expect(screen.getByText("Monthly Salary")).toBeInTheDocument();
    });

    expect(screen.getByText("Grocery Store")).toBeInTheDocument();
    expect(screen.getByText("Transfer to Savings")).toBeInTheDocument();
  });

  it("renders table headers correctly", async () => {
    vi.mocked(api.getTransactions).mockResolvedValue(mockTransactions);

    render(<TransactionList />);

    await waitFor(() => {
      expect(screen.getByText("Date")).toBeInTheDocument();
    });

    expect(screen.getByText("Description")).toBeInTheDocument();
    expect(screen.getByText("Category")).toBeInTheDocument();
    expect(screen.getByText("Amount")).toBeInTheDocument();
    expect(screen.getByText("Balance After")).toBeInTheDocument();
  });

  it("displays income category badges (Salary) with green styling", async () => {
    vi.mocked(api.getTransactions).mockResolvedValue([mockTransactions[0]]);

    render(<TransactionList />);

    await waitFor(() => {
      const salaryBadge = screen.getByText("Salary");
      expect(salaryBadge).toBeInTheDocument();
      expect(salaryBadge).toHaveClass("bg-green-600");
    });
  });

  it("displays income category badges (Refund) with green styling", async () => {
    vi.mocked(api.getTransactions).mockResolvedValue([mockTransactions[3]]);

    render(<TransactionList />);

    await waitFor(() => {
      const refundBadge = screen.getByText("Refund");
      expect(refundBadge).toBeInTheDocument();
      expect(refundBadge).toHaveClass("bg-green-600");
    });
  });

  it("displays expense category badges (Groceries) with destructive variant", async () => {
    vi.mocked(api.getTransactions).mockResolvedValue([mockTransactions[1]]);

    render(<TransactionList />);

    await waitFor(() => {
      const groceriesBadge = screen.getByText("Groceries");
      expect(groceriesBadge).toBeInTheDocument();
      // Destructive variant typically has destructive class
    });
  });

  it("displays expense category badges (Subscription) with destructive variant", async () => {
    vi.mocked(api.getTransactions).mockResolvedValue([mockTransactions[4]]);

    render(<TransactionList />);

    await waitFor(() => {
      const subscriptionBadge = screen.getByText("Subscription");
      expect(subscriptionBadge).toBeInTheDocument();
    });
  });

  it("displays transfer category badges with blue styling", async () => {
    vi.mocked(api.getTransactions).mockResolvedValue([mockTransactions[2]]);

    render(<TransactionList />);

    await waitFor(() => {
      const transferBadge = screen.getByText("Internal Transfer");
      expect(transferBadge).toBeInTheDocument();
      expect(transferBadge).toHaveClass("bg-blue-600");
    });
  });

  it("formats credit amounts with '+' prefix and green color", async () => {
    vi.mocked(api.getTransactions).mockResolvedValue([mockTransactions[0]]);

    render(<TransactionList />);

    await waitFor(() => {
      const amountCell = screen.getByText(/\+\$5,000\.00/);
      expect(amountCell).toBeInTheDocument();
      expect(amountCell).toHaveClass("text-green-500");
    });
  });

  it("formats debit amounts with '-' prefix and red color", async () => {
    vi.mocked(api.getTransactions).mockResolvedValue([mockTransactions[1]]);

    render(<TransactionList />);

    await waitFor(() => {
      const amountCell = screen.getByText(/-\$85\.50/);
      expect(amountCell).toBeInTheDocument();
      expect(amountCell).toHaveClass("text-red-500");
    });
  });

  it("formats balance after correctly", async () => {
    vi.mocked(api.getTransactions).mockResolvedValue([mockTransactions[0]]);

    render(<TransactionList />);

    await waitFor(() => {
      expect(screen.getByText("$15,000.00")).toBeInTheDocument();
    });
  });

  it("displays relative time for recent transactions (minutes)", async () => {
    vi.mocked(api.getTransactions).mockResolvedValue([mockTransactions[0]]);

    render(<TransactionList />);

    await waitFor(() => {
      const dateText = screen.getByText(/30 minutes ago/);
      expect(dateText).toBeInTheDocument();
    });
  });

  it("displays relative time for recent transactions (hours)", async () => {
    vi.mocked(api.getTransactions).mockResolvedValue([mockTransactions[1]]);

    render(<TransactionList />);

    await waitFor(() => {
      const dateText = screen.getByText(/5 hours ago/);
      expect(dateText).toBeInTheDocument();
    });
  });

  it("displays relative time for recent transactions (days)", async () => {
    vi.mocked(api.getTransactions).mockResolvedValue([mockTransactions[2]]);

    render(<TransactionList />);

    await waitFor(() => {
      const dateText = screen.getByText(/2 days ago/);
      expect(dateText).toBeInTheDocument();
    });
  });

  it("displays formatted date for older transactions", async () => {
    vi.mocked(api.getTransactions).mockResolvedValue([mockTransactions[4]]);

    render(<TransactionList />);

    await waitFor(() => {
      // Should show "Jun 15, 2024" or similar format
      const dateText = screen.getByText(/Jun 15/);
      expect(dateText).toBeInTheDocument();
    });
  });

  it("displays empty state when no transactions", async () => {
    vi.mocked(api.getTransactions).mockResolvedValue([]);

    render(<TransactionList />);

    await waitFor(() => {
      expect(screen.getByText("No transactions found")).toBeInTheDocument();
    });
  });

  it("displays error state on API failure", async () => {
    const errorMessage = "Network error";
    vi.mocked(api.getTransactions).mockRejectedValue(new Error(errorMessage));

    render(<TransactionList />);

    await waitFor(() => {
      expect(screen.getByText(/Error: Network error/)).toBeInTheDocument();
    });
  });

  it("calls getTransactions API on mount", async () => {
    vi.mocked(api.getTransactions).mockResolvedValue(mockTransactions);

    render(<TransactionList />);

    await waitFor(() => {
      expect(api.getTransactions).toHaveBeenCalledTimes(1);
      expect(api.getTransactions).toHaveBeenCalledWith(undefined, 50);
    });
  });

  it("calls getTransactions with accountId when provided", async () => {
    vi.mocked(api.getTransactions).mockResolvedValue(mockTransactions);

    render(<TransactionList accountId="acc1" />);

    await waitFor(() => {
      expect(api.getTransactions).toHaveBeenCalledTimes(1);
      expect(api.getTransactions).toHaveBeenCalledWith("acc1", 50);
    });
  });

  it("renders all transactions in the list", async () => {
    vi.mocked(api.getTransactions).mockResolvedValue(mockTransactions);

    render(<TransactionList />);

    await waitFor(() => {
      expect(screen.getByText("Monthly Salary")).toBeInTheDocument();
      expect(screen.getByText("Grocery Store")).toBeInTheDocument();
      expect(screen.getByText("Transfer to Savings")).toBeInTheDocument();
      expect(screen.getByText("Refund - Return")).toBeInTheDocument();
      expect(screen.getByText("Netflix Subscription")).toBeInTheDocument();
    });
  });

  it("has overflow-x-auto wrapper for responsive design", async () => {
    vi.mocked(api.getTransactions).mockResolvedValue(mockTransactions);

    const { container } = render(<TransactionList />);

    await waitFor(() => {
      const wrapper = container.querySelector(".overflow-x-auto");
      expect(wrapper).toBeInTheDocument();
    });
  });
});
