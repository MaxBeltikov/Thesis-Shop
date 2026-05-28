import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../api/client.js'
import { apiErrorMessage } from '../utils/format.js'

const DOC_TYPES = [
  { value: 'кп', label: 'Коммерческое предложение' },
  { value: 'счёт', label: 'Счёт' },
  { value: 'акт', label: 'Акт' },
  { value: 'накладная', label: 'Накладная' },
]

export function DocumentNew() {
  const { orderId } = useParams()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    doc_type: 'кп',
    counterparty_name: 'ООО Контрагент',
    counterparty_inn: '7700000000',
    counterparty_address: 'г. Москва',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function onSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const res = await api.post('/documents/', {
        order: Number(orderId),
        ...form,
      })
      navigate(`/documents/${res.data.id}`)
    } catch (err) {
      setError(apiErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="content">
      <div className="page-header">
        <h1 className="page-title">Новый документ</h1>
        <Link to={`/orders/${orderId}`} className="btn secondary">
          Назад к заказу
        </Link>
      </div>
      {error ? <div className="error banner">{error}</div> : null}
      <form className="panel form" onSubmit={onSubmit}>
        <label className="field">
          <span>Тип документа</span>
          <select value={form.doc_type} onChange={(e) => setForm({ ...form, doc_type: e.target.value })}>
            {DOC_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Контрагент</span>
          <input
            value={form.counterparty_name}
            onChange={(e) => setForm({ ...form, counterparty_name: e.target.value })}
            required
          />
        </label>
        <label className="field">
          <span>ИНН</span>
          <input
            value={form.counterparty_inn}
            onChange={(e) => setForm({ ...form, counterparty_inn: e.target.value })}
            required
          />
        </label>
        <label className="field">
          <span>Адрес</span>
          <textarea
            rows={2}
            value={form.counterparty_address}
            onChange={(e) => setForm({ ...form, counterparty_address: e.target.value })}
            required
          />
        </label>
        <button className="btn" type="submit" disabled={loading}>
          {loading ? 'Создание…' : 'Создать и сгенерировать файлы'}
        </button>
      </form>
    </div>
  )
}
