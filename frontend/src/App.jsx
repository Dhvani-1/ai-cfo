import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import AppLayout from './layouts/AppLayout';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import UploadCenter from './pages/UploadCenter';
import TransactionsPage from './pages/TransactionsPage';
import InvoicesPage from './pages/InvoicesPage';
import AIChat from './pages/AIChat';
import ForecastCenter from './pages/ForecastCenter';
import HealthCenter from './pages/HealthCenter';
import FraudCenter from './pages/FraudCenter';
import TaxCenter from './pages/TaxCenter';
import ReportsCenter from './pages/ReportsCenter';
import Profile from './pages/Profile';
import InsightsPage from './pages/InsightsPage';
import { ToastProvider } from './context/ToastContext';

function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <AuthProvider>
          <Routes>
            {/* Guest Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected Client Routes */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="insights" element={<InsightsPage />} />
              <Route path="upload" element={<UploadCenter />} />
              <Route path="transactions" element={<TransactionsPage />} />
              <Route path="invoices" element={<InvoicesPage />} />
              <Route path="chat" element={<AIChat />} />
              <Route path="forecast" element={<ForecastCenter />} />
              <Route path="health" element={<HealthCenter />} />
              <Route path="fraud" element={<FraudCenter />} />
              <Route path="tax" element={<TaxCenter />} />
              <Route path="reports" element={<ReportsCenter />} />
              <Route path="profile" element={<Profile />} />
            </Route>

            {/* Fallback redirection */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AuthProvider>
      </ToastProvider>
    </BrowserRouter>
  );
}

export default App;
