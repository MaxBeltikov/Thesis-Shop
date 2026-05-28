import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'
import { useAuth } from '../context/AuthContext.jsx'
import { apiErrorMessage } from '../utils/format.js'

export function OrderNew() {
  const navigate = useNavigate()
  const { isManager } = useAuth()
  const [products, setProducts] = useState([])
  const [clientId, setClientId] = useState('')
  const [items, setItems] = useState([{ product: '', quantity: '1', price: '' }])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api.get('/catalog/products/').then((res) => setProducts(res.data.filter((p) => p.is_active)))
  }, [])

  function updateItem(index, field, value) {
    setItems((prev) => {
      const next = [...prev]
      next[index] = { ...next[index], [field]: value }
      if (field === 'product') {
        const p = products.find((x) => String(x.id) === String(value))
        if (p) next[index].price = p.price
      }
      return next
    })
  }

  function addRow() {
    setItems((prev) => [...prev, { product: '', quantity: '1', price: '' }])
  }

  function removeRow(index) {
    setItems((prev) => prev.filter((_, i) => i !== index))
  }

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const payload = {
        items: items.map((row) => ({
          product: Number(row.product),
          quantity: String(row.quantity),
          price: String(row.price),
        })),
      }
      if (isManager && clientId) {
        payload.client = Number(clientId)
      }
      const res = await api.post('/orders/', payload)
      navigate(`/orders/${res.data.id}`)
    } catch (err) {
      setError(apiErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="content">
      <div className="page-header">
        <h1 className="page-title">Новый заказ</h1>
        <Link to="/orders" className="btn secondary">
          Назад
        </Link>
      </div>

      {error ? <div className="error banner">{error}</div> : null}

      <form className="panel form" onSubmit={onSubmit}>
        {isManager ? (
          <label className="field">
            <span>ID клиента (если заказ оформляет менеджер)</span>
            <input
              type="number"
              value={clientId}
              onChange={(e) => setClientId(e.target.value)}
              placeholder="Оставьте пустым — заказ на себя"
            />
          </label>
        ) : null}

        <h2>Позиции</h2>
        {items.map((row, index) => (
          <div key={index} className="item-row">
            <select
              value={row.product}
              onChange={(e) => updateItem(index, 'product', e.target.value)}
              required
            >
              <option value="">Товар…</option>
              {products.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.price} ₽)
                </option>
              ))}
            </select>
            <input
              type="number"
              step="0.01"
              min="0.01"
              placeholder="Кол-во"
              value={row.quantity}
              onChange={(e) => updateItem(index, 'quantity', e.target.value)}
              required
            />
            <input
              type="number"
              step="0.01"
              min="0"
              placeholder="Цена"
              value={row.price}
              onChange={(e) => updateItem(index, 'price', e.target.value)}
              required
            />
            {items.length > 1 ? (
              <button type="button" className="btn secondary btn-sm" onClick={() => removeRow(index)}>
                ×
              </button>
            ) : null}
          </div>
        ))}
        <button type="button" className="btn secondary" onClick={addRow}>
          + Позиция
        </button>
        <button className="btn" type="submit" disabled={loading}>
          {loading ? 'Создание…' : 'Оформить заказ'}
        </button>
      </form>
    </div>
  )
}
