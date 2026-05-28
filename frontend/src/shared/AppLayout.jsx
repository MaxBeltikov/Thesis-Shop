import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { userFio } from '../utils/format.js'

export function AppLayout() {
  const { user, logout, isManager, loading } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  if (loading) {
    return (
      <div className="app-loading">
        <p>Загрузка…</p>
      </div>
    )
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">E‑Commerce</div>
        <nav className="nav">
          <NavLink to="/orders" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
            Заказы
          </NavLink>
          <NavLink to="/catalog" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
            Каталог
          </NavLink>
          {isManager ? (
            <>
              <NavLink to="/action-logs" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
                Журнал
              </NavLink>
              <NavLink to="/reports" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
                Отчёты
              </NavLink>
            </>
          ) : null}
          <NavLink to="/profile" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
            Профиль
          </NavLink>
        </nav>
        <div className="sidebar-footer">
          <div className="user-mini">
            <span className="user-email">{userFio(user)}</span>
            <span className="user-role">{user?.role || '—'}</span>
          </div>
          <button type="button" className="btn secondary btn-sm" onClick={handleLogout}>
            Выйти
          </button>
        </div>
      </aside>
      <main className="main">
        <Outlet />
      </main>
    </div>
  )
}
