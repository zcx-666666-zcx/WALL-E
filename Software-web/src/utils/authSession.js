const LOGIN_USER_KEY = 'loginUserObject'
const USER_ID_KEY = 'Id'
const MANUAL_LOGOUT_KEY = 'walleManualLogoutAt'
const MANUAL_LOGOUT_WINDOW_MS = 5 * 60 * 1000

export function clearAuthSession() {
  localStorage.removeItem(LOGIN_USER_KEY)
  localStorage.removeItem(USER_ID_KEY)
}

export function markManualLogout() {
  sessionStorage.setItem(MANUAL_LOGOUT_KEY, String(Date.now()))
}

export function isManualLogoutInProgress() {
  const raw = sessionStorage.getItem(MANUAL_LOGOUT_KEY)
  if (!raw) return false
  const timestamp = Number(raw)
  if (!Number.isFinite(timestamp)) {
    sessionStorage.removeItem(MANUAL_LOGOUT_KEY)
    return false
  }
  const active = Date.now() - timestamp < MANUAL_LOGOUT_WINDOW_MS
  if (!active) sessionStorage.removeItem(MANUAL_LOGOUT_KEY)
  return active
}

export function clearManualLogoutFlag() {
  sessionStorage.removeItem(MANUAL_LOGOUT_KEY)
}

export function isAuthSilentError(error) {
  return Boolean(error?.__authSilent || error?.code === 'AUTH_SESSION_MISSING')
}

export function logoutLocally() {
  markManualLogout()
  clearAuthSession()
}
