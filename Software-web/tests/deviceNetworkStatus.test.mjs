import test from 'node:test'
import assert from 'node:assert/strict'

let mergeDeviceNetworkStatus
let refreshDeviceNetworkStatuses

test.before(async () => {
  ({ mergeDeviceNetworkStatus, refreshDeviceNetworkStatuses } = await import(
    '../src/utils/deviceNetworkStatus.mjs'
  ))
})

test('merges latest heartbeat IP and online state into a machine', () => {
  const machine = { id: 2, connectionId: 'WALLE_1', robotIp: '192.168.1.2' }
  const status = {
    deviceId: 'WALLE_1',
    lanIp: '10.0.0.8',
    networkName: 'office-wifi',
    online: true,
    lastSeenAt: '2026-07-21T15:00:00'
  }

  const merged = mergeDeviceNetworkStatus(machine, status)

  assert.equal(merged.robotIp, '10.0.0.8')
  assert.deepEqual(merged.networkStatus, status)
  assert.equal(machine.robotIp, '192.168.1.2')
})

test('refreshes every machine without losing one failed query', async () => {
  const machines = [
    { id: 1, connectionId: 'WALLE_1', robotIp: 'old-ip' },
    { id: 2, connectionId: 'WALLE_2', robotIp: 'keep-me' }
  ]
  const fetchStatus = async (deviceId) => {
    if (deviceId === 'WALLE_2') throw new Error('offline')
    return { code: 1, data: { deviceId, lanIp: '10.0.0.8', online: true } }
  }

  const refreshed = await refreshDeviceNetworkStatuses(machines, fetchStatus)

  assert.equal(refreshed[0].robotIp, '10.0.0.8')
  assert.equal(refreshed[0].networkStatus.online, true)
  assert.equal(refreshed[1].robotIp, 'keep-me')
  assert.equal(refreshed[1].networkStatus.online, false)
  assert.equal(refreshed[1].networkStatus.unavailable, true)
})
