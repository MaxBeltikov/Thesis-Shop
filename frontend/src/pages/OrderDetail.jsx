import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client.js'
import { useAuth } from '../context/AuthContext.jsx'
import { StatusBadge } from '../shared/StatusBadge.jsx'
import { apiErrorMessage, docTypeLabel, formatDate, formatMoney } from '../utils/format.js'

const STATUSES = ['новый', 'в работе', 'выполнен', 'отменён']

export function OrderDetail() {
  const { id } = useParams()
  const { isManager } = useAuth()
  const [order, setOrder] = useState(null)
  const [documents, setDocuments] = useState([])
  const [status, setStatus] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  async function load() {
    setLoading(true)
    setError('')
    try {
      const [orderRes, docsRes] = await Promise.all([
        api.get(`/orders/${id}/`),
        api.get(`/orders/${id}/documents/`),
      ])
      setOrder(orderRes.data)
      setStatus(orderRes.data.status)
      setDocuments(docsRes.data)
    } catch (err) {
      setError(apiErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [id])

  async function saveStatus(e) {
    e.preventDefault()
    setSaving(true)
    try {
      await api.patch(`/orders/${id}/`, { status })
      await load()
    } catch (err) {
      setError(apiErrorMessage(err))
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="content"><p className="muted">Загрузка…</p></div>
  if (!order) return <div className="content"><div className="error banner">{error || 'Заказ не найден'}</div></div>

  return (
    <div className="content">
      <div className="page-header">
        <h1 className="page-title">Заказ {order.number}</h1>
        <Link to="/orders" className="btn secondary">
          К списку
        </Link>
      </div>

      {error ? <div className="error banner">{error}</div> : null}

      <div className="panel grid-2">
        <div>
          <dl className="dl">
            <dt>Клиент</dt>
            <dd>{order.client_email}</dd>
            <dt>Статус</dt>
            <dd>
              <StatusBadge status={order.status} />
            </dd>
            <dt>Сумма</dt>
            <dd>{formatMoney(order.total_amount)}</dd>
            <dt>Создан</dt>
            <dd>{formatDate(order.created_at)}</dd>
          </dl>
          {isManager ? (
            <form className="inline-form" onSubmit={saveStatus}>
              <select value={status} onChange={(e) => setStatus(e.target.value)}>
                {STATUSES.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
              <button className="btn btn-sm" type="submit" disabled={saving}>
                Обновить статус
              </button>
            </form>
          ) : null}
        </div>
        <div>
          <h2>Позиции</h2>
          <table className="table table-compact">
            <thead>
              <tr>
                <th>Товар</th>
                <th>Кол-во</th>
                <th>Цена</th>
                <th>Сумма</th>
              </tr>
            </thead>
            <tbody>
              {(order.items || []).map((item) => (
                <tr key={item.id}>
                  <td>{item.product_name || item.product}</td>
                  <td>{item.quantity}</td>
                  <td>{formatMoney(item.price)}</td>
                  <td>{formatMoney(item.amount)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="panel">
        <div className="page-header inner">
          <h2>Документы</h2>
          <Link to={`/orders/${id}/documents/new`} className="btn btn-sm">
            Создать документ
          </Link>
        </div>
        {documents.length === 0 ? (
          <p className="muted">Документов нет.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Номер</th>
                <th>Связь</th>
                <th>Тип</th>
                <th>Статус</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {documents.map((d) => (
                <tr key={d.id}>
                  <td>{d.number}</td>
                  <td className="muted small">
                    {d.parent ? `← ${d.parent_number || d.parent}` : '—'}
                  </td>
                  <td>{d.doc_type_display || docTypeLabel(d.doc_type)}</td>
                  <td>
                    <StatusBadge status={d.status} />
                  </td>
                  <td>
                    <Link to={`/documents/${d.id}`}>Открыть</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
