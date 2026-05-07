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

  function formatRegisterError(data) {
    if (!data) return 'Ошибка регистрации'
    if (typeof data === 'string') return data
    if (data.detail) return data.detail

    const messages = []

    if (Array.isArray(data.email) && data.email.length) {
      if (String(data.email[0]).includes('already exists')) {
        messages.push('Пользователь с таким email уже существует')
      } else {
        messages.push(data.email[0])
      }
    }

    if (Array.isArray(data.password) && data.password.length) {
      if (String(data.password[0]).toLowerCase().includes('at least 6')) {
        messages.push('Пароль должен быть минимум 6 символов')
      } else {
        messages.push(data.password[0])
      }
    }

    return messages.length ? messages.join('. ') : JSON.stringify(data)
  }

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
      setError(formatRegisterError(err?.response?.data))
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

