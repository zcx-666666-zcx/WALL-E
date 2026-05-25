//import { data } from "element-plus/es/locales.mjs";
import request from "../utils/request";
import cozerequest from "../utils/cozeRequest"

export const LoginApi = (loginInfo)=>{return request.post('/login',loginInfo)}
export const RegisApi = (RegisInfo)=>{return request.post('/users/register',RegisInfo)}

export const GetElementListApi = (userId)=>{return request.get(`/events/search/${userId}`)}
export const GetContactsListApi = (userId)=>{return request.get(`/contractUser/search/${userId}`)}
export const GetMachineListApi = (userId)=>{return request.get(`/contractMachine/search/${userId}`)}
export const GetCommandListApi = (data)=>{return request.post("/command/search",data)}
export const GetIdApi = (username)=>{return request.get(`/users/getId/${username}`)}
export const GetNameApi = (id)=>{return request.get(`/users/getName/${id}`)}

export const DeleteElementApi = (data)=>{return request.delete('/events/delete',data)}
export const DeleteContractUserApi = (data)=>{return request.delete('/contractUser/delete',data)}
export const DeleteMachinesApi = (data)=>{return request.delete('/contractMachine/delete',data)}

export const EditElementApi = (data)=>{return request.post('/events/searchOne',data)}

export const UpdateElementApi = (data)=>{return request.put('/events/update',data)}

export const AddElementApi = (Element)=>{return request.post('/events/add',Element)}
export const AddContractUserApi = (data)=>{return request.post('/contractUser/add',data)}
export const AddMachineApi = (data)=>{return request.post('/contractMachine/add',data)}

export const getRateApi = (deviceId)=>{return request.get(`/healthy/getRate/${deviceId}`)}
export const getHumidityApi = (deviceId)=>{return request.get(`/healthy/getHumidity/${deviceId}`)}
export const getBreatheApi = (deviceId)=>{return request.get(`/healthy/getBreathe/${deviceId}`)}
export const getTemperatureApi = (deviceId)=>{return request.get(`/healthy/getTemperature/${deviceId}`)}
export const getFallApi = (deviceId)=>{return request.get(`/healthy/getFall/${deviceId}`)}

export const SetStyleOnCozeApi = (data)=>{return cozerequest.post('/v1/workflow/stream_run',data)}

// ── 机器人代理 API ──
export const RobotMotorApi    = (data) => request.post('/robot/motor', data)
export const RobotServoApi    = (data) => request.post('/robot/servo', data)
export const RobotAnimateApi  = (data) => request.post('/robot/animate', data)
export const RobotSettingsApi = (data) => request.post('/robot/settings', data)
export const RobotIpApi       = (machineId) => request.get(`/robot/robotIp/${machineId}`)

export const DeleteAccountApi = () => request.delete('/users/deleteAccount')
