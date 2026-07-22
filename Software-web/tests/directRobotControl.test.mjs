import test from 'node:test'
import assert from 'node:assert/strict'

let buildDirectRobotControlUrl
try {
  ({ buildDirectRobotControlUrl } = await import('../src/views/drive/directRobotControl.mjs'))
} catch {
  buildDirectRobotControlUrl = undefined
}

test('uses the latest heartbeat LAN IP for direct robot control', () => {
  assert.equal(typeof buildDirectRobotControlUrl, 'function')
  const machine = { robotIp: '192.168.1.20' }
  const status = { lanIp: '10.0.0.8' }

  assert.equal(buildDirectRobotControlUrl(machine, status, 5000), 'http://10.0.0.8:5000')
})

test('falls back to the stored robot IP when heartbeat is unavailable', () => {
  const machine = { robotIp: '192.168.1.20' }

  assert.equal(buildDirectRobotControlUrl(machine, null, 5000), 'http://192.168.1.20:5000')
})

test('returns null when no robot IP is available', () => {
  assert.equal(buildDirectRobotControlUrl({}, {}, 5000), null)
})

test('uses the configured robot HTTP port', () => {
  assert.equal(
    buildDirectRobotControlUrl({ robotIp: '192.168.1.20' }, null, 5050),
    'http://192.168.1.20:5050'
  )
})

test('falls back to the stored IP when the heartbeat IP is invalid', () => {
  const machine = { robotIp: '192.168.1.20' }
  const status = { lanIp: '127.0.0.1@evil.example' }

  assert.equal(buildDirectRobotControlUrl(machine, status, 5000), 'http://192.168.1.20:5000')
})

test('rejects an invalid stored robot IP', () => {
  assert.equal(
    buildDirectRobotControlUrl({ robotIp: 'bad ip' }, null, 5000),
    null
  )
})

test('falls back when a heartbeat IP contains ambiguous leading zeroes', () => {
  assert.equal(
    buildDirectRobotControlUrl(
      { robotIp: '192.168.1.20' },
      { lanIp: '08.0.0.1' },
      5000
    ),
    'http://192.168.1.20:5000'
  )
})
