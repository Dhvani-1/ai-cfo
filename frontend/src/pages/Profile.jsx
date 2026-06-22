import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import SectionHeader from '../components/SectionHeader';
import ProfileCard from '../components/ProfileCard';
import { useToast } from '../context/ToastContext';

const Profile = () => {
  const { user, setUser } = useAuth();
  const { showToast } = useToast();
  
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Total Income / Expenses state
  const [totals, setTotals] = useState({ revenue: 0, expenses: 0 });
  const [statsLoading, setStatsLoading] = useState(true);

  useEffect(() => {
    const fetchProfileData = async () => {
      try {
        const [meRes, pnlRes] = await Promise.all([
          api.get('/me'),
          api.get('/profit-loss')
        ]);
        
        // Sync user in AuthContext to keep statistics updated
        setUser(meRes.data);
        setTotals(pnlRes.data);
      } catch (err) {
        console.error('Failed to load profile details:', err);
        showToast('Failed to sync latest profile stats.', 'error');
      } finally {
        setStatsLoading(false);
      }
    };
    
    fetchProfileData();
  }, [setUser, showToast]);

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    
    try {
      await api.post('/change-password', {
        old_password: oldPassword,
        new_password: newPassword
      });
      showToast('Password updated successfully. Please use your new credentials next time.', 'success');
      setOldPassword('');
      setNewPassword('');
    } catch (err) {
      console.error(err);
      const errMsg = err.response?.data?.detail || 'Failed to update password. Password must be >=8 characters with a digit.';
      setError(errMsg);
      showToast(errMsg, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <SectionHeader 
        title="My Profile" 
        subtitle="Manage personal credentials and view aggregate financial summaries."
      />

      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        {/* Profile Card Summary Panel */}
        <div className="md:col-span-1">
          {statsLoading ? (
            <div className="rounded-xl border border-slate-200 bg-white p-12 text-center shadow-xs flex justify-center items-center">
              <svg className="h-5 w-5 animate-spin text-indigo-650" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
          ) : (
            <ProfileCard 
              user={user} 
              totalIncome={totals.revenue} 
              totalExpenses={totals.expenses} 
            />
          )}
        </div>

        {/* Password Management Form */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs md:col-span-2 text-left">
          <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-4 mb-4">Security Settings</h3>
          <p className="text-xs text-slate-400">Update account access credentials.</p>

          <form onSubmit={handlePasswordChange} className="mt-6 space-y-4">
            {error && (
              <div className="rounded-lg bg-rose-50 border border-rose-100 p-3 text-xs font-semibold text-rose-600">
                {error}
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide">Old Password</label>
              <input
                type="password"
                required
                value={oldPassword}
                onChange={(e) => setOldPassword(e.target.value)}
                className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 placeholder-slate-405 focus:border-indigo-500 focus:outline-hidden focus:ring-1 focus:ring-indigo-500 text-xs"
                placeholder="••••••••"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide">New Password</label>
              <input
                type="password"
                required
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 placeholder-slate-405 focus:border-indigo-500 focus:outline-hidden focus:ring-1 focus:ring-indigo-500 text-xs"
                placeholder="Min. 8 characters, with 1 digit"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="flex w-full justify-center rounded-lg bg-indigo-600 px-4 py-2.5 text-xs font-semibold text-white shadow-xs hover:bg-indigo-500 disabled:opacity-50 select-none cursor-pointer"
            >
              {loading ? 'Updating credentials...' : 'Change Password'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Profile;
