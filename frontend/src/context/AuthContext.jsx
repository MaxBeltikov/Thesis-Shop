import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { api } from '../api/client.js'
import { clearTokens, hasAccessToken } from '../auth/tokens.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const refreshUser = useCallback(async () => {
    if (!hasAccessToken()) {
      setUser(null)
      setLoading(false)
      return
    }
    try {
      const res = await api.get('/auth/me/')
      setUser(res.data)
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refreshUser()
  }, [refreshUser])

  function logout() {
    clearTokens()
    setUser(null)
  }

  const isManager = user?.role === 'manager' || user?.role === 'admin'

  return (
    <AuthContext.Provider value={{ user, loading, refreshUser, logout, isManager }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
