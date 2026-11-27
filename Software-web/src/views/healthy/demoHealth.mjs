const demoValues = {
  rate: [75, 2, 0],
  humidity: [50, 1, 1],
  breathe: [16, 1, 0],
  temperature: [36.5, 0.2, 1],
}

export function healthRowsOrDemo(response, field, now = Date.now()) {
  if (response?.code !== 1) throw new Error(response?.msg || '健康数据请求失败')
  const rows = response.data?.rows || []
  if (rows.length) {
    return [...rows]
      .sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt))
      .map(row => [new Date(row.createdAt).toLocaleTimeString(), row[field]])
  }
  const [base, amplitude, digits] = demoValues[field]
  const end = Math.floor(now / 2000) * 2000
  return Array.from({ length: 20 }, (_, i) => {
    const timestamp = end - (19 - i) * 2000
    const value = base + amplitude * Math.sin(timestamp / 9000)
    return [new Date(timestamp).toLocaleTimeString(), Number(value.toFixed(digits))]
  })
}

export function demoFall(response) {
  if (response?.code !== 1) throw new Error(response?.msg || '健康数据请求失败')
  return response.data?.fall ?? false
}
