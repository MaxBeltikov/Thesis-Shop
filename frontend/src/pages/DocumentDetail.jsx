import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../api/client.js'
import { useAuth } from '../context/AuthContext.jsx'
import { StatusBadge } from '../shared/StatusBadge.jsx'
import { apiErrorMessage, docTypeLabel, formatDate, mediaUrl } from '../utils/format.js'

const NEXT_DOC_TYPE = { 'кп': 'счёт', 'счёт': 'акт' }

export function DocumentDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user, isManager } = useAuth()
  const [doc, setDoc] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [actionLoading, setActionLoading] = useState('')
  const [signPassword, setSignPassword] = useState('')
  const [showSign, setShowSign] = useState(false)

  async function load() {
    setLoading(true)
    setError('')
    try {
      const res = await api.get(`/documents/${id}/`)
      setDoc(res.data)
    } catch (err) {
      setError(apiErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [id])

  async function runAction(name, request) {
    setActionLoading(name)
    setError('')
    try {
      await request()
      setShowSign(false)
      setSignPassword('')
      await load()
    } catch (err) {
      setError(apiErrorMessage(err))
    } finally {
      setActionLoading('')
    }
  }

  if (loading) return <div className="content"><p className="muted">Загрузка…</p></div>
  if (!doc) return <div className="content"><div className="error banner">{error || 'Не найден'}</div></div>

  const canSign = doc.status !== 'подписан' && doc.status !== 'отклонён'
  const canSend = doc.status === 'черновик'
  const pdfLink = mediaUrl(doc.pdf_file)
  const docxLink = mediaUrl(doc.docx_file)
  const nextType = NEXT_DOC_TYPE[doc.doc_type]

  return (
    <div className="content">
      <div className="page-header">
        <h1 className="page-title">Документ {doc.number}</h1>
        <Link to={`/orders/${doc.order}`} className="btn secondary">
          К заказу
        </Link>
      </div>

      {error ? <div className="error banner">{error}</div> : null}

      <div className="panel">
        <dl className="dl">
          <dt>Тип</dt>
          <dd>{doc.doc_type_display || docTypeLabel(doc.doc_type)}</dd>
          <dt>Заказ</dt>
          <dd>
            <Link to={`/orders/${doc.order}`}>{doc.order_number || doc.order}</Link>
          </dd>
          {doc.parent ? (
            <>
              <dt>Основан на</dt>
              <dd>
                <Link to={`/documents/${doc.parent}`}>
                  {doc.parent_number || `Документ #${doc.parent}`}
                </Link>
              </dd>
            </>
          ) : null}
          <dt>Статус</dt>
          <dd>
            <StatusBadge status={doc.status} />
          </dd>
          <dt>Контрагент</dt>
          <dd>
            {doc.counterparty_name}, ИНН {doc.counterparty_inn}
            <br />
            {doc.counterparty_address}
          </dd>
          <dt>Создан</dt>
          <dd>{formatDate(doc.created_at)}</dd>
          {doc.signed_at ? (
            <>
              <dt>Подписан</dt>
              <dd>
                {formatDate(doc.signed_at)} ({doc.signed_by_email})
              </dd>
            </>
          ) : null}
        </dl>

        {doc.children && doc.children.length ? (
          <div className="muted" style={{ marginTop: 10 }}>
            Создано на основе этого документа:
            <ul style={{ margin: '6px 0 0', paddingLeft: 18 }}>
              {doc.children.map((c) => (
                <li key={c.id}>
                  <Link to={`/documents/${c.id}`}>{c.number}</Link> — {c.doc_type_display} ({c.status_display})
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        <div className="file-links">
          {docxLink ? (
            <a href={docxLink} target="_blank" rel="noreferrer" className="btn secondary">
              Скачать DOCX
            </a>
          ) : null}
          {pdfLink ? (
            <a href={pdfLink} target="_blank" rel="noreferrer" className="btn secondary">
              Скачать PDF
            </a>
          ) : null}
          <button
            type="button"
            className="btn secondary"
            disabled={!!actionLoading}
            onClick={() => runAction('generate', () => api.post(`/documents/${id}/generate/`))}
          >
            Перегенерировать
          </button>
        </div>

        <div className="action-bar">
          {canSend ? (
            <button
              type="button"
              className="btn"
              disabled={!!actionLoading}
              onClick={() => runAction('send', () => api.post(`/documents/${id}/send/`))}
            >
              Отправить
            </button>
          ) : null}
          {canSign ? (
            <>
              {!showSign ? (
                <button type="button" className="btn" onClick={() => setShowSign(true)}>
                  Подписать (ЭЦП)
                </button>
              ) : (
                <form
                  className="sign-form"
                  onSubmit={(e) => {
                    e.preventDefault()
                    runAction('sign', () =>
                      api.post(`/documents/${id}/sign/`, { password: signPassword }),
                    )
                  }}
                >
                  <input
                    type="password"
                    placeholder="Пароль для подписи"
                    value={signPassword}
                    onChange={(e) => setSignPassword(e.target.value)}
                    required
                  />
                  <button className="btn" type="submit" disabled={!!actionLoading}>
                    Подтвердить
                  </button>
                  <button type="button" className="btn secondary" onClick={() => setShowSign(false)}>
                    Отмена
                  </button>
                </form>
              )}
            </>
          ) : null}
          {isManager && nextType ? (
            <button
              type="button"
              className="btn secondary"
              disabled={!!actionLoading}
              onClick={async () => {
                setActionLoading('next')
                setError('')
                try {
                  const res = await api.post(`/documents/${id}/create-next/`)
                  // Важно: не вызываем load() для старого id — сразу переходим на новый документ.
                  navigate(`/documents/${res.data.id}`)
                } catch (err) {
                  setError(apiErrorMessage(err))
                } finally {
                  setActionLoading('')
                }
              }}
            >
              Следующий в цепочке (КП→счёт→акт)
            </button>
          ) : null}
          {isManager && canSign ? (
            <button
              type="button"
              className="btn secondary danger-outline"
              disabled={!!actionLoading}
              onClick={() => {
                const reason = prompt('Причина отклонения (необязательно)') || ''
                runAction('reject', () => api.post(`/documents/${id}/reject/`, { reason }))
              }}
            >
              Отклонить
            </button>
          ) : null}
        </div>
        {showSign ? (
          <p className="muted small">Имитация ЭЦП: введите ваш пароль ({user?.email}).</p>
        ) : null}
      </div>
    </div>
  )
}
