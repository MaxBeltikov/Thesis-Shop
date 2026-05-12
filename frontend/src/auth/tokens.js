export function saveTokens({ access, refresh }) {
  localStorage.setItem('accessToken', access)
  localStorage.setItem('refreshToken', refresh)
}

export function clearTokens() {
  localStorage.removeItem('accessToken')
  localStorage.removeItem('refreshToken')
}

export function hasAccessToken() {
  return Boolean(localStorage.getItem('accessToken'))
}
