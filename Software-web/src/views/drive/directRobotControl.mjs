export function buildDirectRobotControlUrl(machine, networkStatus, configuredPort = 5000) {
  const heartbeatIp = normalizeIpv4(networkStatus?.lanIp)
  const storedIp = normalizeIpv4(machine?.robotIp)
  const ip = heartbeatIp || storedIp
  if (!ip) return null

  const parsedPort = Number(configuredPort)
  const port = Number.isInteger(parsedPort) && parsedPort > 0 && parsedPort <= 65535
    ? parsedPort
    : 5000
  return `http://${ip}:${port}`
}

function normalizeIpv4(value) {
  const candidate = String(value || '').trim()
  const octets = candidate.split('.')
  if (octets.length !== 4) return null
  if (!octets.every(octet => /^(0|[1-9]\d{0,2})$/.test(octet) && Number(octet) <= 255)) return null
  return candidate
}
