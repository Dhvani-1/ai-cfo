import React, { useState, useEffect } from 'react';
import api from '../services/api';
import SectionHeader from '../components/SectionHeader';
import SearchBar from '../components/SearchBar';
import Pagination from '../components/Pagination';
import TransactionTable from '../components/TransactionTable';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { useNavigate } from 'react-router-dom';

const TransactionsPage = () => {
  const navigate = useNavigate();
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Search, sorting, and pagination state
  const [searchQuery, setSearchQuery] = useState('');
  const [sortField, setSortField] = useState('date');
  const [sortDirection, setSortDirection] = useState('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const res = await api.get('/transactions');
        setTransactions(res.data);
      } catch (err) {
        console.error(err);
        setError('Failed to load transaction statement lists.');
      } finally {
        setLoading(false);
      }
    };
    fetchTransactions();
  }, []);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
    setCurrentPage(1); // Reset page on sort change
  };

  // Filter transactions based on SearchQuery
  const filteredTxs = transactions.filter((tx) => {
    const descMatch = tx.description?.toLowerCase().includes(searchQuery.toLowerCase());
    const catMatch = tx.category?.toLowerCase().includes(searchQuery.toLowerCase());
    const typeMatch = tx.type?.toLowerCase().includes(searchQuery.toLowerCase());
    return descMatch || catMatch || typeMatch;
  });

  // Sort filtered transactions
  const sortedTxs = [...filteredTxs].sort((a, b) => {
    let valA = a[sortField];
    let valB = b[sortField];

    // Handle null/undefined values safely
    if (valA === undefined || valA === null) valA = '';
    if (valB === undefined || valB === null) valB = '';

    if (sortField === 'amount') {
      return sortDirection === 'asc' ? valA - valB : valB - valA;
    }

    // String/Date comparisons
    return sortDirection === 'asc'
      ? String(valA).localeCompare(String(valB))
      : String(valB).localeCompare(String(valA));
  });

  // Paginated sorted transactions
  const paginatedTxs = sortedTxs.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const handleItemsPerPageChange = (size) => {
    setItemsPerPage(size);
    setCurrentPage(1);
  };

  if (loading) return <div className="flex h-96 items-center justify-center"><LoadingSpinner /></div>;
  if (error) return <div className="rounded-xl bg-rose-50 p-6 text-center text-rose-600 font-semibold border border-rose-100">{error}</div>;

  return (
    <div className="space-y-6">
      <SectionHeader 
        title="Transactions Ledger" 
        subtitle="Complete record of categorized cash inflows and outflows."
      />

      {transactions.length === 0 ? (
        <EmptyState
          title="No transactions imported"
          message="We couldn't find any financial statement records in your database ledger. Please upload a spreadsheet statement to analyze Cash Flow metrics."
          actionLabel="Go to Upload Center"
          onAction={() => navigate('/upload')}
        />
      ) : (
        <div className="space-y-4">
          {/* Filters Tool Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <SearchBar
              value={searchQuery}
              onChange={(val) => {
                setSearchQuery(val);
                setCurrentPage(1); // Reset page on search change
              }}
              placeholder="Search by description or category..."
            />
          </div>

          {/* Transactions Table */}
          <TransactionTable
            transactions={paginatedTxs}
            sortField={sortField}
            sortDirection={sortDirection}
            onSort={handleSort}
          />

          {/* Pagination Toolbar */}
          <Pagination
            currentPage={currentPage}
            totalItems={sortedTxs.length}
            itemsPerPage={itemsPerPage}
            onPageChange={handlePageChange}
            onItemsPerPageChange={handleItemsPerPageChange}
          />
        </div>
      )}
    </div>
  );
};

export default TransactionsPage;
