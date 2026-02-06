'use client';

import { useState, useEffect } from 'react';
import { adminService, AdminPayout, PayoutsResponse } from '@/lib/admin-service';
import Link from 'next/link';

export default function AdminPayouts() {
  const [payouts, setPayouts] = useState<AdminPayout[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<'PENDING' | 'PROCESSING' | 'COMPLETED' | 'CANCELLED' | ''>('');
  const [offset, setOffset] = useState(0);
  const limit = 20;

  useEffect(() => {
    loadPayouts();
  }, [statusFilter, offset]);

  const loadPayouts = async () => {
    try {
      setLoading(true);
      const params: any = { limit, offset };
      if (statusFilter) params.status = statusFilter;

      const data = await adminService.getPayouts(params);
      setPayouts(data.payouts);
      setTotal(data.total);
    } catch (error) {
      console.error('Failed to load payouts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (payoutId: string) => {
    if (!confirm('Approve this payout request?')) return;

    try {
      await adminService.approvePayout(payoutId);
      loadPayouts();
    } catch (error) {
      console.error('Failed to approve payout:', error);
      alert('Failed to approve payout');
    }
  };

  const handleComplete = async (payoutId: string) => {
    const transactionRef = prompt('Enter transaction reference:');
    if (!transactionRef) return;

    try {
      await adminService.completePayout(payoutId, transactionRef);
      loadPayouts();
    } catch (error) {
      console.error('Failed to complete payout:', error);
      alert('Failed to complete payout');
    }
  };

  const handleReject = async (payoutId: string) => {
    const reason = prompt('Enter rejection reason:');
    if (!reason) return;

    try {
      await adminService.rejectPayout(payoutId, reason);
      loadPayouts();
    } catch (error) {
      console.error('Failed to reject payout:', error);
      alert('Failed to reject payout');
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PENDING':
        return 'bg-yellow-100 text-yellow-800';
      case 'PROCESSING':
        return 'bg-blue-100 text-blue-800';
      case 'COMPLETED':
        return 'bg-green-100 text-green-800';
      case 'CANCELLED':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <Link href="/admin" className="text-purple-600 hover:text-purple-700 text-sm mb-2 inline-block">
                ← Back to Dashboard
              </Link>
              <h1 className="text-3xl font-bold text-gray-900">Payout Management</h1>
              <p className="mt-1 text-gray-600">Manage instructor payout requests</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
              <select
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value as any);
                  setOffset(0);
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="">All Statuses</option>
                <option value="PENDING">Pending</option>
                <option value="PROCESSING">Processing</option>
                <option value="COMPLETED">Completed</option>
                <option value="CANCELLED">Cancelled</option>
              </select>
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              {total} {total === 1 ? 'Payout' : 'Payouts'}
            </h2>
          </div>

          {loading ? (
            <div className="p-12 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
            </div>
          ) : payouts.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              No payouts found
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Instructor</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Method</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Requested</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {payouts.map((payout) => (
                    <tr key={payout.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="font-medium text-gray-900">
                          {payout.currency} {payout.amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {payout.instructor_id.slice(0, 8)}...
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {payout.payout_method || 'N/A'}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(payout.status)}`}>
                          {payout.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        <div className="space-y-1">
                          <div>{formatDate(payout.requested_at)}</div>
                          {payout.completed_at && (
                            <div className="text-xs text-gray-400">
                              Completed: {formatDate(payout.completed_at)}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm space-x-2">
                        {payout.status === 'PENDING' && (
                          <>
                            <button
                              onClick={() => handleApprove(payout.id)}
                              className="text-green-600 hover:text-green-700 font-medium"
                            >
                              Approve
                            </button>
                            <button
                              onClick={() => handleReject(payout.id)}
                              className="text-red-600 hover:text-red-700 font-medium"
                            >
                              Reject
                            </button>
                          </>
                        )}
                        {payout.status === 'PROCESSING' && (
                          <button
                            onClick={() => handleComplete(payout.id)}
                            className="text-blue-600 hover:text-blue-700 font-medium"
                          >
                            Complete
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination */}
          {total > limit && (
            <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
              <button
                onClick={() => setOffset(Math.max(0, offset - limit))}
                disabled={offset === 0}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <span className="text-sm text-gray-700">
                Showing {offset + 1} - {Math.min(offset + limit, total)} of {total}
              </span>
              <button
                onClick={() => setOffset(offset + limit)}
                disabled={offset + limit >= total}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
