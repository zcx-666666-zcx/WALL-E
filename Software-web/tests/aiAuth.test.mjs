import test from 'node:test'
import assert from 'node:assert/strict'
import { aiFetch } from '../src/utils/aiAuth.mjs'

test('AI requests carry the current session token', async () => {
  const storage = { getItem: () => JSON.stringify({ token: 'example-token' }) }
  let request
  await aiFetch('/ai/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' } },
    { storage, fetchImpl: async (url, options) => { request = { url, options }; return { ok: true } } })
  assert.equal(request.options.headers.token, 'example-token')
  assert.equal(request.options.headers['Content-Type'], 'application/json')
})

test('AI requests fail locally when there is no session', async () => {
  const storage = { getItem: () => null }
  await assert.rejects(() => aiFetch('/ai/chat', {}, { storage, fetchImpl: async () => ({}) }), /登录/)
})

test('AI rejects an expired or invalid session with a login message', async () => {
  const storage = { getItem: () => JSON.stringify({ token: 'expired' }) }
  await assert.rejects(() => aiFetch('/ai/chat', {}, {
    storage, fetchImpl: async () => ({ status: 401, ok: false })
  }), /登录.*过期/)
})
