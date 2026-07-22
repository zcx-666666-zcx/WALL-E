export function readStoredUsername(storage = globalThis.localStorage) {
  try {
    const raw = storage?.getItem('loginUserObject')
    if (!raw) return ''
    const user = JSON.parse(raw)
    return String(user?.username || user?.name || '')
  } catch {
    return ''
  }
}

export function runStartupTasks(tasks) {
  return Promise.allSettled(tasks.map((task) => task()))
}
