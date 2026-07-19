import test from 'node:test'
import assert from 'node:assert/strict'

let fetchCameraFrame
try {
  ({ fetchCameraFrame } = await import('../src/views/drive/cameraFrame.mjs'))
} catch {
  fetchCameraFrame = undefined
}

test('camera frame request sends the logged-in user token', async () => {
  assert.equal(typeof fetchCameraFrame, 'function')
  const calls = []
  const fetchImpl = async (url, options) => {
    calls.push({ url, options })
    return { ok: true, status: 200, blob: async () => new Blob(['jpeg']) }
  }
  const storage = {
    getItem: () => JSON.stringify({ token: 'user-jwt' })
  }

  const blob = await fetchCameraFrame({
    baseUrl: 'http://server.example/api',
    machineId: 2,
    fetchImpl,
    storage
  })

  assert.equal(blob.size, 4)
  assert.equal(calls[0].url, 'http://server.example/api/robot/camera-frame/2')
  assert.equal(calls[0].options.headers.token, 'user-jwt')
})

test('camera frame request treats no-content as waiting', async () => {
  const fetchImpl = async () => ({ ok: true, status: 204 })
  const storage = { getItem: () => JSON.stringify({ token: 'user-jwt' }) }

  const blob = await fetchCameraFrame({
    baseUrl: '/api',
    machineId: 2,
    fetchImpl,
    storage
  })

  assert.equal(blob, null)
})
