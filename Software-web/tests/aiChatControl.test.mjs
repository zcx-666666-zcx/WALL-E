import test from 'node:test'
import assert from 'node:assert/strict'

let buildAiChatSetting
let readStoredUsername
let runStartupTasks
try {
  ({ buildAiChatSetting, readStoredUsername, runStartupTasks } = await import('../src/views/new_agent/aiChatControl.mjs'))
} catch {
  buildAiChatSetting = undefined
}

test('builds an enable command for the selected robot', () => {
  assert.equal(typeof buildAiChatSetting, 'function')
  assert.deepEqual(buildAiChatSetting(42, true), {
    machineId: 42,
    type: 'aiChat',
    value: 'Active'
  })
})

test('builds a disable command for the selected robot', () => {
  assert.deepEqual(buildAiChatSetting(42, false), {
    machineId: 42,
    type: 'aiChat',
    value: 'Offline'
  })
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
