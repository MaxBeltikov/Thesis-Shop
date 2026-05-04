import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'

export function Register() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [role, setRole] = useState('client')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.post('/auth/register/', {
        email,
        password,
        first_name: firstName,
        last_name: lastName,
        role,
      })
      navigate('/login')
    } catch (err) {
      const data = err?.response?.data
      const msg =
        data?.detail ||
        (data && typeof data === 'object' ? JSON.stringify(data) : '') ||
        'Ошибка регистрации'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <div className="card">
        <h1>Регистрация</h1>
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
              autoComplete="new-password"
            />
          </label>

          <label className="field">
            <span>Имя</span>
            <input value={firstName} onChange={(e) => setFirstName(e.target.value)} />
          </label>

          <label className="field">
            <span>Фамилия</span>
            <input value={lastName} onChange={(e) => setLastName(e.target.value)} />
          </label>

          <label className="field">
            <span>Роль</span>
            <select value={role} onChange={(e) => setRole(e.target.value)}>
              <option value="client">client</option>
              <option value="manager">manager</option>
              <option value="admin">admin</option>
            </select>
          </label>

          {error ? <div className="error">{error}</div> : null}

          <button className="btn" type="submit" disabled={loading}>
            {loading ? 'Создаём…' : 'Создать аккаунт'}
          </button>
        </form>

        <p className="muted">
          Уже есть аккаунт? <Link to="/login">Войти</Link>
        </p>
      </div>
    </div>
  )
}

