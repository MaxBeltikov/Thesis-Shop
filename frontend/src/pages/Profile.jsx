import { useAuth } from '../context/AuthContext.jsx'

export function Profile() {
  const { user } = useAuth()

  return (
    <div className="content">
      <h1 className="page-title">Профиль</h1>
      <div className="panel">
        <dl className="dl">
          <dt>Email</dt>
          <dd>{user?.email}</dd>
          <dt>Роль</dt>
          <dd>
            <span className="role-pill">{user?.role}</span>
          </dd>
          <dt>Имя</dt>
          <dd>
            {user?.first_name || '—'} {user?.last_name || ''}
          </dd>
        </dl>
        {user?.role === 'client' ? (
          <p className="muted">
            Для назначения роли менеджера обратитесь к администратору системы.
          </p>
        ) : null}
      </div>
    </div>
  )
}
