export function createMotorSender(send, timers = globalThis, onError = () => {}) {
  let pending = []
  let active = null
  let inFlight = false
  let timer = null

  function flush() {
    if (inFlight || !pending.length) return
    const command = pending.shift()
    inFlight = true
    Promise.resolve().then(() => send(command)).then(result => {
      if (result && result.code === 0) throw new Error(result.msg || '遥控指令发送失败')
    }).catch(error => {
      if (active && active.machineId === command.machineId) stop()
      onError(error)
    }).finally(() => {
      inFlight = false
      flush()
    })
  }

  function queue(command) {
    const stopCommand = command.stickX === 0 && command.stickY === 0
    if (stopCommand) {
      pending = pending.filter(item => item.machineId !== command.machineId)
      pending.push(command)
    } else {
      const last = pending[pending.length - 1]
      if (last && last.machineId === command.machineId && (last.stickX !== 0 || last.stickY !== 0)) {
        pending[pending.length - 1] = command
      } else {
        pending.push(command)
      }
    }
    flush()
  }

  function stop() {
    if (timer !== null) timers.clearInterval(timer)
    timer = null
    if (active) queue({ machineId: active.machineId, stickX: 0, stickY: 0 })
    active = null
  }

  function move(machineId, x, y) {
    if (!machineId) return
    if (active && active.machineId !== machineId) stop()
    active = { machineId, stickX: +x.toFixed(2), stickY: +y.toFixed(2) }
    queue(active)
    if (timer === null) timer = timers.setInterval(() => { if (active) queue(active) }, 250)
  }

  return { move, stop }
}
