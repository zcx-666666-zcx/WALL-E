export async function fetchCameraFrame({ baseUrl, machineId, fetchImpl = fetch, storage = localStorage }) {
  const rawUser = storage?.getItem('loginUserObject')
  let token = null
  try {
    token = rawUser ? JSON.parse(rawUser)?.token : null
  } catch {
    token = null
  }
  if (!token) throw new Error('auth session missing')

  const response = await fetchImpl(
    `${baseUrl.replace(/\/$/, '')}/robot/camera-frame/${machineId}`,
    { headers: { token }, cache: 'no-store' }
  )
  if (response.status === 204) return null
  if (!response.ok) throw new Error(`camera frame request failed: ${response.status}`)
  return response.blob()
}
