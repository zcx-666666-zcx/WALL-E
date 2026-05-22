import { ElMessage, ElMessageBox } from 'element-plus'

export const toast = {
  success(msg) { ElMessage({ message: msg, type: 'success', duration: 2000, center: true }) },
  warning(msg) { ElMessage({ message: msg, type: 'warning', duration: 2500, center: true }) },
  error(msg)   { ElMessage({ message: msg, type: 'error', duration: 3000, center: true }) },
  info(msg)    { ElMessage({ message: msg, type: 'info', duration: 2000, center: true }) },
}

export async function confirm(msg, title = '提示', opts = {}) {
  try {
    await ElMessageBox.confirm(msg, title, {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      center: true,
      ...opts,
    })
    return true
  } catch {
    return false
  }
}
