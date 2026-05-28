export function StatusBadge({ status }) {
  const cls = `badge badge-${(status || '').replace(/\s/g, '-')}`
  const labels = {
    черновик: 'Черновик',
    отправлен: 'Отправлен',
    подписан: 'Подписан',
    'отклонён': 'Отклонён',
    новый: 'Новый',
    выполнен: 'Выполнен',
  }
  return <span className={cls}>{labels[status] || status}</span>
}
