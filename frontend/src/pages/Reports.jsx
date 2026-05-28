import { useState } from 'react'
import { downloadReport } from '../utils/downloads.js'
import { apiErrorMessage } from '../utils/format.js'

export function Reports() {
  const [error, setError] = useState('')
  const [loading, setLoading] = useState('')

  async function handleDownload(path, filename, key) {
    setLoading(key)
    setError('')
    try {
      await downloadReport(path, filename)
    } catch (err) {
      setError(apiErrorMessage(err))
    } finally {
      setLoading('')
    }
  }

  return (
    <div className="content">
      <h1 className="page-title">Отчёты Excel</h1>
      {error ? <div className="error banner">{error}</div> : null}
      <div className="panel cards-row">
        <div className="mini-card">
          <h2>Заказы</h2>
          <p className="muted">Экспорт всех заказов в .xlsx</p>
          <button
            type="button"
            className="btn"
            disabled={loading === 'orders'}
            onClick={() => handleDownload('/reports/orders/export/', 'orders_report.xlsx', 'orders')}
          >
            {loading === 'orders' ? 'Загрузка…' : 'Скачать'}
          </button>
        </div>
        <div className="mini-card">
          <h2>Документы</h2>
          <p className="muted">Экспорт всех документов в .xlsx</p>
          <button
            type="button"
            className="btn"
            disabled={loading === 'documents'}
            onClick={() =>
              handleDownload('/reports/documents/export/', 'documents_report.xlsx', 'documents')
            }
          >
            {loading === 'documents' ? 'Загрузка…' : 'Скачать'}
          </button>
        </div>
      </div>
    </div>
  )
}
