import { Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext.jsx'
import { ActionLogs } from './pages/ActionLogs.jsx'
import { Catalog } from './pages/Catalog.jsx'
import { DocumentDetail } from './pages/DocumentDetail.jsx'
import { DocumentNew } from './pages/DocumentNew.jsx'
import { Login } from './pages/Login.jsx'
import { OrderDetail } from './pages/OrderDetail.jsx'
import { OrderNew } from './pages/OrderNew.jsx'
import { Orders } from './pages/Orders.jsx'
import { Profile } from './pages/Profile.jsx'
import { Register } from './pages/Register.jsx'
import { Reports } from './pages/Reports.jsx'
import { AppLayout } from './shared/AppLayout.jsx'
import { RequireAuth } from './shared/RequireAuth.jsx'

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/orders" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        element={
          <RequireAuth>
            <AuthProvider>
              <AppLayout />
            </AuthProvider>
          </RequireAuth>
        }
      >
        <Route path="/orders" element={<Orders />} />
        <Route path="/orders/new" element={<OrderNew />} />
        <Route path="/orders/:id" element={<OrderDetail />} />
        <Route path="/orders/:orderId/documents/new" element={<DocumentNew />} />
        <Route path="/catalog" element={<Catalog />} />
        <Route path="/documents/:id" element={<DocumentDetail />} />
        <Route path="/action-logs" element={<ActionLogs />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/dashboard" element={<Navigate to="/profile" replace />} />
      </Route>
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

export default function App() {
  return <AppRoutes />
}
