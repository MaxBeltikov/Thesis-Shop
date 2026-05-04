import { Navigate, useLocation } from 'react-router-dom'
import { hasAccessToken } from '../auth/tokens.js'

export function RequireAuth({ children }) {
  const location = useLocation()
  if (!hasAccessToken()) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }
  return children
}

