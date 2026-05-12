import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

export const api = axios.create({
  baseURL: API_BASE_URL,
})

function getTokens() {
  const access = localStorage.getItem('accessToken')
  const refresh = localStorage.getItem('refreshToken')
  return { access, refresh }
}

function setAccessToken(access) {
  if (access) localStorage.setItem('accessToken', access)
}

function clearTokens() {
  localStorage.removeItem('accessToken')
  localStorage.removeItem('refreshToken')
}

api.interceptors.request.use((config) => {
  const { access } = getTokens()
  if (access) config.headers.Authorization = `Bearer ${access}`
  return config
})

let refreshPromise = null

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error?.config
    const status = error?.response?.status

    if (
      status !== 401 ||
      !original ||
      original._retry ||
      original._skipAuthRefresh ||
      String(original?.url || '').includes('/auth/refresh/')
    ) {
      throw error
    }

    original._retry = true

    const { refresh } = getTokens()
    if (!refresh) {
      clearTokens()
      throw error
    }

    if (!refreshPromise) {
      refreshPromise = api
        .post('/auth/refresh/', { refresh }, { _skipAuthRefresh: true })
        .then((r) => r.data.access)
        .finally(() => {
          refreshPromise = null
        })
    }

    try {
      const newAccess = await refreshPromise
      setAccessToken(newAccess)
      original.headers = original.headers || {}
      original.headers.Authorization = `Bearer ${newAccess}`
      return api.request(original)
    } catch (e) {
      clearTokens()
      throw e
    }
  },
)
