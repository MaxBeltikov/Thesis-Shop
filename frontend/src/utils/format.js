const DOC_TYPES = {
  кп: 'Коммерческое предложение',
  'счёт': 'Счёт',
  акт: 'Акт',
  накладная: 'Накладная',
}

const STATUS_LABELS = {
  черновик: 'Черновик',
  отправлен: 'Отправлен',
  подписан: 'Подписан',
  'отклонён': 'Отклонён',
}

export function docTypeLabel(type) {
  return DOC_TYPES[type] || type
}

export function statusLabel(status) {
  return STATUS_LABELS[status] || status
}

export function formatMoney(value) {
  const n = Number(value)
  if (Number.isNaN(n)) return value
  return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB' }).format(n)
}

/** ФИО для отображения в интерфейсе (span.user-email). Без email. */
export function userFio(user) {
  if (!user) return ''
  const first = (user.first_name || '').trim()
  const last = (user.last_name || '').trim()
  if (last && first) return `${last} ${first}`
  if (last) return last
  if (first) return first
  return ''
}

export function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('ru-RU')
}

export function apiErrorMessage(err, fallback = 'Ошибка запроса') {
  const data = err?.response?.data
  if (!data) return fallback
  if (typeof data === 'string') return data
  if (data.detail) return String(data.detail)
  const parts = []
  for (const [key, val] of Object.entries(data)) {
    if (Array.isArray(val)) parts.push(`${key}: ${val.join(', ')}`)
    else parts.push(`${key}: ${val}`)
  }
  return parts.length ? parts.join('; ') : fallback
}

export const MEDIA_BASE = 'http://127.0.0.1:8000'

/** Путь в БД: documents/file.pdf → URL: /media/documents/file.pdf */
export function mediaUrl(path) {
  if (!path) return null
  if (path.startsWith('http')) return path
  const clean = path.replace(/^\//, '')
  if (clean.startsWith('media/')) {
    return `${MEDIA_BASE}/${clean}`
  }
  return `${MEDIA_BASE}/media/${clean}`
}
