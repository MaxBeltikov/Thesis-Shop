import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'
import { saveTokens } from '../auth/tokens.js'

export function Login() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await api.post('/auth/login/', { email, password })
      saveTokens(res.data)
      navigate('/orders')
    } catch (err) {
      const msg =
        err?.response?.data?.detail ||
        (typeof err?.response?.data === 'string' ? err.response.data : '') ||
        'Ошибка входа'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <div className="card">
        <h1>Вход</h1>
        <form onSubmit={onSubmit} className="form">
          <label className="field">
            <span>Email</span>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </label>

          <label className="field">
            <span>Пароль</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </label>

          {error ? <div className="error">{error}</div> : null}

          <button className="btn" type="submit" disabled={loading}>
            {loading ? 'Входим…' : 'Войти'}
          </button>
        </form>

        <p className="muted">
          Нет аккаунта? <Link to="/register">Регистрация</Link>
        </p>
      </div>
    </div>
  )
}

