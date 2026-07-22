import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

let readStoredUsername
let runStartupTasks
try {
  ({ readStoredUsername, runStartupTasks } = await import('../src/views/new_agent/agentStartup.mjs'))
} catch {
  readStoredUsername = undefined
}

test('AI settings page has no hardware chat switch', async () => {
  const source = await readFile(
    new URL('../src/views/new_agent/Agent_new.vue', import.meta.url),
    'utf8'
  )

  assert.doesNotMatch(source, /aiChat|硬件语音聊天/)
})

test('uses the logged-in username while the user API is unavailable', () => {
  assert.equal(typeof readStoredUsername, 'function')
  const storage = {
    getItem: () => JSON.stringify({ username: 'test' })
  }

  assert.equal(readStoredUsername(storage), 'test')
})

test('runs page startup tasks independently when one request fails', async () => {
  assert.equal(typeof runStartupTasks, 'function')
  const calls = []
  const results = await runStartupTasks([
    async () => { calls.push('user'); throw new Error('user API down') },
    async () => { calls.push('backend'); return 'online' },
    async () => { calls.push('machines'); return [] }
  ])

  assert.deepEqual(calls, ['user', 'backend', 'machines'])
  assert.equal(results[0].status, 'rejected')
  assert.equal(results[1].status, 'fulfilled')
  assert.equal(results[2].status, 'fulfilled')
})
