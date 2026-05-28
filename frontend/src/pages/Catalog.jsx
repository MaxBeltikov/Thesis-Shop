import { useEffect, useState } from 'react'
import { api } from '../api/client.js'
import { useAuth } from '../context/AuthContext.jsx'
import { apiErrorMessage, formatMoney } from '../utils/format.js'

const emptyProduct = { name: '', description: '', price: '', unit: 'шт.', is_active: true }

export function Catalog() {
  const { isManager } = useAuth()
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [query, setQuery] = useState('')
  const [form, setForm] = useState(emptyProduct)
  const [editingId, setEditingId] = useState(null)
  const [saving, setSaving] = useState(false)
  const [showEditor, setShowEditor] = useState(false)

  async function load(search = '') {
    setLoading(true)
    setError('')
    try {
      const res = await api.get('/catalog/products/', {
        params: search ? { search } : undefined,
      })
      setProducts(res.data)
    } catch (err) {
      setError(apiErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  function startEdit(p) {
    setShowEditor(true)
    setEditingId(p.id)
    setForm({
      name: p.name,
      description: p.description || '',
      price: p.price,
      unit: p.unit,
      is_active: p.is_active,
    })
  }

  function cancelEdit() {
    setEditingId(null)
    setForm(emptyProduct)
    setShowEditor(false)
  }

  async function saveProduct(e) {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      const payload = {
        ...form,
        price: String(form.price),
      }
      if (editingId) {
        await api.patch(`/catalog/products/${editingId}/`, payload)
      } else {
        await api.post('/catalog/products/', payload)
      }
      cancelEdit()
      await load()
    } catch (err) {
      setError(apiErrorMessage(err))
    } finally {
      setSaving(false)
    }
  }

  async function removeProduct(id) {
    if (!confirm('Удалить товар?')) return
    try {
      await api.delete(`/catalog/products/${id}/`)
      await load()
    } catch (err) {
      setError(apiErrorMessage(err))
    }
  }

  return (
    <div className="content">
      <div className="page-header">
        <h1 className="page-title">Каталог товаров и услуг</h1>
      </div>

      {error ? <div className="error banner">{error}</div> : null}

      <div className="panel">
        <div className="form form-grid">
          <label className="field field-full">
            <span>Поиск по названию</span>
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Например: ноутбук"
            />
          </label>
          <div className="form-actions field-full">
            <button
              type="button"
              className="btn secondary"
              onClick={() => load(query.trim())}
              disabled={loading}
            >
              Найти
            </button>
            <button
              type="button"
              className="btn"
              onClick={() => {
                setQuery('')
                load('')
              }}
              disabled={loading}
            >
              Сброс
            </button>
          </div>
        </div>
      </div>

      {isManager ? (
        <div className="panel">
          <div className="page-header inner">
            <h2>{editingId ? 'Редактировать товар' : 'Новый товар'}</h2>
            {!showEditor ? (
              <button type="button" className="btn" onClick={() => setShowEditor(true)}>
                Добавить товар
              </button>
            ) : (
              <button type="button" className="btn secondary" onClick={cancelEdit} disabled={saving}>
                Скрыть
              </button>
            )}
          </div>

          {showEditor ? (
            <form className="form form-grid" onSubmit={saveProduct}>
              <label className="field">
                <span>Название</span>
                <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
              </label>
              <label className="field">
                <span>Цена</span>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={form.price}
                  onChange={(e) => setForm({ ...form, price: e.target.value })}
                  required
                />
              </label>
              <label className="field">
                <span>Ед.</span>
                <input value={form.unit} onChange={(e) => setForm({ ...form, unit: e.target.value })} />
              </label>
              <label className="field field-check">
                <input
                  type="checkbox"
                  checked={form.is_active}
                  onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
                />
                <span>Активен</span>
              </label>
              <label className="field field-full">
                <span>Описание</span>
                <textarea
                  rows={2}
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                />
              </label>
              <div className="form-actions field-full">
                <button className="btn" type="submit" disabled={saving}>
                  {saving ? 'Сохранение…' : editingId ? 'Сохранить' : 'Добавить'}
                </button>
                {showEditor ? (
                  <button type="button" className="btn secondary" onClick={cancelEdit} disabled={saving}>
                    Отмена
                  </button>
                ) : null}
              </div>
            </form>
          ) : null}
        </div>
      ) : null}

      <div className="panel">
        {loading ? (
          <p className="muted">Загрузка…</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Название</th>
                <th>Цена</th>
                <th>Ед.</th>
                <th>Статус</th>
                {isManager ? <th></th> : null}
              </tr>
            </thead>
            <tbody>
              {products.map((p) => (
                <tr key={p.id}>
                  <td>
                    <strong>{p.name}</strong>
                    {p.description ? <div className="muted small">{p.description}</div> : null}
                  </td>
                  <td>{formatMoney(p.price)}</td>
                  <td>{p.unit}</td>
                  <td>{p.is_active ? 'В продаже' : 'Снят'}</td>
                  {isManager ? (
                    <td className="actions-cell">
                      <button type="button" className="link-btn" onClick={() => startEdit(p)}>
                        Изменить
                      </button>
                      <button type="button" className="link-btn danger" onClick={() => removeProduct(p.id)}>
                        Удалить
                      </button>
                    </td>
                  ) : null}
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {!loading && products.length === 0 ? (
          <p className="muted">{query.trim() ? 'Ничего не найдено.' : 'Товаров пока нет.'}</p>
        ) : null}
      </div>
    </div>
  )
}
