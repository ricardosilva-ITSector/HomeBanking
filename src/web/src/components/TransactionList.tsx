import { useState, useEffect } from "react";
import { getTransactions } from "@/services/api";
import type { Transaction } from "@/types/api";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

/**
 * Props for TransactionList component.
 */
interface TransactionListProps {
  accountId?: string;
}

/**
 * Maps transaction category to badge variant and classes.
 * @param category - Transaction category
 * @returns Badge variant
 */
function getCategoryVariant(category: string): {
  variant: "default" | "destructive" | "secondary";
  className?: string;
} {
  // Income categories (green)
  const incomeCategories = ["Salary", "Refund"];
  if (incomeCategories.includes(category)) {
    return { variant: "default", className: "bg-green-600 hover:bg-green-700" };
  }

  // Expense categories (red/destructive)
  const expenseCategories = [
    "Groceries",
    "Utilities",
    "Entertainment",
    "Subscription",
    "Shopping",
    "Dining",
    "Transport",
  ];
  if (expenseCategories.includes(category)) {
    return { variant: "destructive" };
  }

  // Transfer categories (blue/secondary)
  if (category === "Internal Transfer") {
    return { variant: "secondary", className: "bg-blue-600 hover:bg-blue-700" };
  }

  // Default
  return { variant: "default" };
}

/**
 * Formats currency amount.
 * @param amount - Amount to format
 * @returns Formatted currency string
 */
function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
}

/**
 * Formats date to relative time or local date string.
 * @param dateString - ISO date string
 * @returns Formatted date string
 */
function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  // If within last 24 hours, show relative time
  if (diffHours < 1) {
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    if (diffMinutes < 1) {
      return "Just now";
    }
    return `${diffMinutes} minute${diffMinutes > 1 ? "s" : ""} ago`;
  } else if (diffHours < 24) {
    return `${diffHours} hour${diffHours > 1 ? "s" : ""} ago`;
  } else if (diffDays < 7) {
    return `${diffDays} day${diffDays > 1 ? "s" : ""} ago`;
  }

  // Otherwise show formatted date
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: date.getFullYear() !== now.getFullYear() ? "numeric" : undefined,
  });
}

/**
 * TransactionList component displays a table of transactions.
 * Fetches and displays transactions with optional filtering by account.
 */
export function TransactionList({ accountId }: TransactionListProps) {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getTransactions(accountId, 50); // Limit to 50 recent transactions
        setTransactions(data);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load transactions"
        );
      } finally {
        setLoading(false);
      }
    };

    fetchTransactions();
  }, [accountId]);

  // Loading state
  if (loading) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-500">Loading transactions...</p>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">Error: {error}</p>
      </div>
    );
  }

  // Empty state
  if (transactions.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-500">No transactions found</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="text-slate-600">Date</TableHead>
            <TableHead className="text-slate-600">Description</TableHead>
            <TableHead className="text-slate-600">Category</TableHead>
            <TableHead className="text-right text-slate-600">Amount</TableHead>
            <TableHead className="text-right text-slate-600">
              Balance After
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {transactions.map((transaction) => {
            const categoryStyle = getCategoryVariant(transaction.category);
            const isCredit = transaction.type === "Credit";
            const amountPrefix = isCredit ? "+" : "-";
            const amountColor = isCredit ? "text-green-500" : "text-red-500";

            return (
              <TableRow key={transaction.id}>
                <TableCell className="text-slate-500">
                  {formatDate(transaction.date)}
                </TableCell>
                <TableCell className="text-slate-800">
                  {transaction.description}
                </TableCell>
                <TableCell>
                  <Badge
                    variant={categoryStyle.variant}
                    className={categoryStyle.className}
                  >
                    {transaction.category}
                  </Badge>
                </TableCell>
                <TableCell className={`text-right font-medium ${amountColor}`}>
                  {amountPrefix}
                  {formatCurrency(Math.abs(transaction.amount))}
                </TableCell>
                <TableCell className="text-right text-slate-700">
                  {formatCurrency(transaction.balanceAfter)}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}
