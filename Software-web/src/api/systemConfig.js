import request from '../utils/request'

export const GetPublicSystemConfigApi = () => request.get('/system-config/public')
export const GetSystemConfigApi = () => request.get('/system-config')
export const UpdateSystemConfigApi = (configs) => request.put('/system-config', configs)
