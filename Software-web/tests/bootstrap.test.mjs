import test from 'node:test'
import assert from 'node:assert/strict'

let bootstrapApp
try {
  ({ bootstrapApp } = await import('../src/bootstrap.mjs'))
} catch {
  bootstrapApp = undefined
}

test('loads public config before mounting the app', async () => {
  assert.equal(typeof bootstrapApp, 'function')
  const calls = []

  await bootstrapApp(
    async () => { calls.push('config') },
    () => { calls.push('mount') }
  )

  assert.deepEqual(calls, ['config', 'mount'])
})

test('mounts the app even when public config is unavailable', async () => {
  const calls = []

  await bootstrapApp(
    async () => { calls.push('config'); throw new Error('backend unavailable') },
    () => { calls.push('mount') }
  )

  assert.deepEqual(calls, ['config', 'mount'])
})

