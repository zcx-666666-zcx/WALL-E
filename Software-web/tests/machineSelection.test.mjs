import test from 'node:test'
import assert from 'node:assert/strict'

let selectPreferredMachine
try {
  ({ selectPreferredMachine } = await import('../src/views/drive/machineSelection.mjs'))
} catch {
  selectPreferredMachine = undefined
}

test('prefers the standard WALL-E device over an older duplicate', () => {
  assert.equal(typeof selectPreferredMachine, 'function')
  const machines = [
    { id: 1, connectionId: 'kCx33ym0Dt' },
    { id: 2, connectionId: 'WALLE_1' }
  ]

  assert.equal(selectPreferredMachine(machines)?.id, 2)
})

test('accepts the deployed WALEE spelling during migration', () => {
  assert.equal(typeof selectPreferredMachine, 'function')
  const machines = [
    { id: 1, connectionId: 'kCx33ym0Dt' },
    { id: 2, connectionId: 'WALEE_1' }
  ]

  assert.equal(selectPreferredMachine(machines)?.id, 2)
})

test('prefers WALLE over WALEE when both records exist', () => {
  const machines = [
    { id: 2, connectionId: 'WALEE_1' },
    { id: 3, connectionId: 'WALLE_1' }
  ]

  assert.equal(selectPreferredMachine(machines)?.id, 3)
})
