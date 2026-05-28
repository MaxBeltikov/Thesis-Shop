import { useEffect, useState } from 'react'
import { api } from '../api/client.js'
import { apiErrorMessage, formatDate } from '../utils/format.js'

export function ActionLogs() {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function load() {
      try {
        const res = await api.get('/action-logs/')
        setLogs(res.data)
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
      <h1 className="page-title">Журнал действий</h1>
      {error ? <div className="error banner">{error}</div> : null}
      <div className="panel">
        {loading ? (
          <p className="muted">Загрузка…</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Время</th>
                <th>Пользователь</th>
                <th>Действие</th>
                <th>Сущность</th>
                <th>ID</th>
                <th>IP</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((row) => (
                <tr key={row.id}>
                  <td>{formatDate(row.created_at)}</td>
                  <td>{row.user_email || '—'}</td>
                  <td>{row.action}</td>
                  <td>{row.entity_type}</td>
                  <td>{row.entity_id}</td>
                  <td>{row.ip_address || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {!loading && logs.length === 0 ? <p className="muted">Записей нет.</p> : null}
      </div>
    </div>
  )
}
