import test from 'node:test'
import assert from 'node:assert/strict'
import { createMotorSender } from '../src/views/drive/motorSender.mjs'

test('reports an application error and stops refreshing motion', async () => {
  let tick, cleared = false
  const errors = []
  const sender = createMotorSender(() => Promise.resolve({ code: 0, msg: '机器人离线' }),
    { setInterval: callback => { tick = callback; return 1 }, clearInterval: () => { cleared = true } },
    error => errors.push(error.message))
  sender.move(3, 0.5, 0)
  await new Promise(resolve => setImmediate(resolve))
  assert.deepEqual(errors, ['机器人离线', '机器人离线'])
  assert.equal(cleared, true)
  tick()
})

test('keeps refreshing held motion and always sends stop after an in-flight command', async () => {
  let finishFirst, tick
  const calls = []
  const sender = createMotorSender(payload => {
    calls.push(payload)
    if (calls.length === 1) return new Promise(resolve => { finishFirst = resolve })
    return Promise.resolve()
  }, { setInterval: callback => { tick = callback; return 1 }, clearInterval: () => {} })
  sender.move(3, 0.5, 0.2)
  await Promise.resolve()
  tick()
  sender.stop()
  finishFirst()
  await new Promise(resolve => setImmediate(resolve))
  assert.deepEqual(calls, [
    { machineId: 3, stickX: 0.5, stickY: 0.2 },
    { machineId: 3, stickX: 0, stickY: 0 },
  ])
})

test('sends fresh motion at intervals while held', async () => {
  let tick
  const calls = []
  const sender = createMotorSender(payload => { calls.push(payload); return Promise.resolve() },
    { setInterval: callback => { tick = callback; return 1 }, clearInterval: () => {} })
  sender.move(3, 0.2, 0.4)
  await new Promise(resolve => setImmediate(resolve))
  tick()
  await new Promise(resolve => setImmediate(resolve))
  assert.equal(calls.length, 2)
  sender.stop()
})

test('stops previous device before commanding a newly selected device', async () => {
  let finishFirst
  const calls = []
  const sender = createMotorSender(payload => {
    calls.push(payload)
    return calls.length === 1 ? new Promise(resolve => { finishFirst = resolve }) : Promise.resolve()
  }, { setInterval: () => 1, clearInterval: () => {} })
  sender.move(3, 0.5, 0)
  await Promise.resolve()
  sender.move(4, 0.2, 0)
  finishFirst()
  await new Promise(resolve => setImmediate(resolve))
  assert.deepEqual(calls, [
    { machineId: 3, stickX: 0.5, stickY: 0 },
    { machineId: 3, stickX: 0, stickY: 0 },
    { machineId: 4, stickX: 0.2, stickY: 0 },
  ])
  sender.stop()
})
