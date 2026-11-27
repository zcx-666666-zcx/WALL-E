import test from 'node:test'
import assert from 'node:assert/strict'
import { createCandidateBuffer } from '../src/views/video/iceCandidates.mjs'

test('candidates are buffered until remote description is set', async () => {
  const added = []
  const peer = { remoteDescription: null, addIceCandidate: async value => added.push(value) }
  const buffer = createCandidateBuffer(() => peer)
  await buffer.add({ candidate: 'first' })
  assert.deepEqual(added, [])
  peer.remoteDescription = { type: 'offer' }
  await buffer.flush()
  await buffer.add({ candidate: 'second' })
  assert.deepEqual(added, [{ candidate: 'first' }, { candidate: 'second' }])
})

test('clearing candidates prevents old call candidates leaking into a new call', async () => {
  const added = []
  const peer = { remoteDescription: null, addIceCandidate: async value => added.push(value) }
  const buffer = createCandidateBuffer(() => peer)
  await buffer.add({ candidate: 'old' })
  buffer.clear()
  peer.remoteDescription = { type: 'offer' }
  await buffer.flush()
  assert.deepEqual(added, [])
})
