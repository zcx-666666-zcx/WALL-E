export function mergeDeviceNetworkStatus(machine, status) {
  if (!machine || !status) return machine
  return {
    ...machine,
    robotIp: status.lanIp || machine.robotIp,
    networkStatus: status
  }
}

export async function refreshDeviceNetworkStatuses(machines, fetchStatus) {
  if (!Array.isArray(machines) || machines.length === 0) return []
  return Promise.all(machines.map(async (machine) => {
    if (!machine?.connectionId) return machine
    try {
      const response = await fetchStatus(machine.connectionId)
      if (response?.code === 1) return mergeDeviceNetworkStatus(machine, response.data)
      return markNetworkStatusUnavailable(machine)
    } catch {
      return markNetworkStatusUnavailable(machine)
    }
  }))
}

function markNetworkStatusUnavailable(machine) {
  return {
    ...machine,
    networkStatus: {
      ...(machine.networkStatus || {}),
      online: false,
      unavailable: true
    }
  }
}
