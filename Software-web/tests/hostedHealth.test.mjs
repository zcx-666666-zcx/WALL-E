import test from 'node:test'
import assert from 'node:assert/strict'
import { routerBase } from '../src/router/routerBase.mjs'
import { healthRowsOrDemo, demoFall } from '../src/views/healthy/demoHealth.mjs'

test('resolves a relative build base against the document base URL', () => {
  assert.equal(routerBase('./', 'https://example.org/walle/'), '/walle/')
  assert.equal(routerBase('./', 'http://localhost:5173/'), '/')
  assert.equal(routerBase('/app/', 'https://example.org/walle/'), '/app/')
})

test('shows demonstration values when the API has no readings', () => {
  const points = healthRowsOrDemo({ code: 1, data: { rows: [] } }, 'rate', 1700000000000)
  assert.equal(points.length, 20)
  assert.ok(points.every(point => Number.isFinite(point[1]) && point[1] >= 70 && point[1] <= 80))
  assert.equal(demoFall({ code: 1, data: null }), false)
  const temperature = healthRowsOrDemo({ code: 1, data: { rows: [] } }, 'temperature', 1700000000000)
  assert.ok(temperature.every(point => point[1] >= 24 && point[1] <= 26))
})

test('uses returned readings and does not disguise API errors as demo data', () => {
  const result = { code: 1, data: { rows: [{ createdAt: '2026-11-27T10:00:00Z', rate: 81 }] } }
  assert.equal(healthRowsOrDemo(result, 'rate', 1700000000000)[0][1], 81)
  assert.throws(() => healthRowsOrDemo({ code: 0, msg: 'forbidden' }, 'rate', 1700000000000))
})
