export async function aiFetch(url, options = {}, dependencies = {}) {
  const storage = dependencies.storage || localStorage
  let token = ''
  try { token = JSON.parse(storage.getItem('loginUserObject') || '{}').token || '' } catch { /* missing session */ }
  if (!token) throw new Error('请先登录')
  const response = await (dependencies.fetchImpl || fetch)(url, {
    ...options,
    headers: { ...(options.headers || {}), token },
  })
  if (response.status === 401) throw new Error('登录已过期，请重新登录')
  if (response.status === 403) throw new Error('没有权限访问该用户的数据')
  return response
}
