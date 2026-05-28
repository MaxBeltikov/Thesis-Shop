import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client.js'
import { useAuth } from '../context/AuthContext.jsx'
import { StatusBadge } from '../shared/StatusBadge.jsx'
import { apiErrorMessage, formatDate, formatMoney } from '../utils/format.js'

export function Orders() {
  const { isManager } = useAuth()
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [query, setQuery] = useState('')

  useEffect(() => {
    async function load(search = '') {
      setLoading(true)
      try {
        const res = await api.get('/orders/', {
          params: search ? { search } : undefined,
        })
        setOrders(res.data)
      } catch (err) {
        setError(apiErrorMessage(err))
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  return (
    <div className="content">
      <div className="page-header">
        <h1 className="page-title">Заказы</h1>
        <Link to="/orders/new" className="btn">
          Новый заказ
        </Link>
      </div>

      {error ? <div className="error banner">{error}</div> : null}

      <div className="panel">
        <div className="form form-grid">
          <label className="field field-full">
            <span>Поиск</span>
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Номер заказа, статус, email клиента…"
            />
          </label>
          <div className="form-actions field-full">
            <button
              type="button"
              className="btn secondary"
              onClick={async () => {
                setLoading(true)
                setError('')
                try {
                  const res = await api.get('/orders/', { params: query.trim() ? { search: query.trim() } : undefined })
                  setOrders(res.data)
                } catch (err) {
                  setError(apiErrorMessage(err))
                } finally {
                  setLoading(false)
                }
              }}
              disabled={loading}
            >
              Найти
            </button>
            <button
              type="button"
              className="btn"
              onClick={async () => {
                setQuery('')
                setLoading(true)
                setError('')
                try {
                  const res = await api.get('/orders/')
                  setOrders(res.data)
                } catch (err) {
                  setError(apiErrorMessage(err))
                } finally {
                  setLoading(false)
                }
              }}
              disabled={loading}
            >
              Сброс
            </button>
          </div>
        </div>
      </div>

      <div className="panel">
        {loading ? (
          <p className="muted">Загрузка…</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Номер</th>
                {isManager ? <th>Клиент</th> : null}
                <th>Статус</th>
                <th>Сумма</th>
                <th>Создан</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {orders.map((o) => (
                <tr key={o.id}>
                  <td>
                    <Link to={`/orders/${o.id}`}>{o.number}</Link>
                  </td>
                  {isManager ? <td>{o.client_email || o.client}</td> : null}
                  <td>
                    <StatusBadge status={o.status} />
                  </td>
                  <td>{formatMoney(o.total_amount)}</td>
                  <td>{formatDate(o.created_at)}</td>
                  <td>
                    <Link to={`/orders/${o.id}`} className="link-btn">
                      Открыть
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {!loading && orders.length === 0 ? (
          <p className="muted">{query.trim() ? 'Ничего не найдено.' : 'Заказов пока нет.'}</p>
        ) : null}
      </div>
    </div>
  )
}
