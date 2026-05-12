import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'
import { clearTokens } from '../auth/tokens.js'

export function Dashboard() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let mounted = true
    async function load() {
      setError('')
      setLoading(true)
      try {
        const res = await api.get('/auth/me/')
        if (mounted) setEmail(res.data.email)
      } catch (err) {
        if (!mounted) return
        setError('Не удалось загрузить профиль')
      } finally {
        if (mounted) setLoading(false)
      }
    }
    load()
    return () => {
      mounted = false
    }
  }, [])

  function logout() {
    clearTokens()
    navigate('/login')
  }

  return (
    <div className="page">
      <div className="card">
        <h1>Профиль</h1>
        {loading ? (
          <p className="muted">Загрузка…</p>
        ) : error ? (
          <div className="error">{error}</div>
        ) : (
          <p>
            Добро пожаловать, <b>{email}</b>
          </p>
        )}

        <button className="btn secondary" type="button" onClick={logout}>
          Выйти
        </button>
      </div>
    </div>
  )
}

