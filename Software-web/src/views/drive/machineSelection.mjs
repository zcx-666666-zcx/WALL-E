const STANDARD_DEVICE_ID = 'WALLE_1'
const LEGACY_DEVICE_ID = 'WALEE_1'

export function selectPreferredMachine(machines) {
  if (!Array.isArray(machines) || machines.length === 0) return null
  const normalized = machines.map(machine => ({
    machine,
    id: String(machine?.connectionId || '').trim().toUpperCase()
  }))
  return normalized.find(item => item.id === STANDARD_DEVICE_ID)?.machine
    || normalized.find(item => item.id === LEGACY_DEVICE_ID)?.machine
    || machines[0]
}
