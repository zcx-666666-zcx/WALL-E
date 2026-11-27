export function createCandidateBuffer(getPeer) {
  let pending = []
  return {
    async add(candidate) {
      if (!candidate) return
      const peer = getPeer()
      if (!peer?.remoteDescription) pending.push(candidate)
      else await peer.addIceCandidate(candidate)
    },
    async flush() {
      const peer = getPeer()
      if (!peer?.remoteDescription) return
      const queued = pending
      pending = []
      for (const candidate of queued) await peer.addIceCandidate(candidate)
    },
    clear() { pending = [] },
  }
}
