//import { data } from "element-plus/es/locales.mjs";
import request from "../utils/request";

export const LoginApi = (loginInfo)=>{return request.post('/login',loginInfo)}

export const GetElementListApi = (userId)=>{return request.get(`/events/search/${userId}`)}
export const GetContactsListApi = (userId)=>{return request.get(`/contractUser/search/${userId}`)}
export const GetMachineListApi = (userId)=>{return request.get(`/contractMachine/search/${userId}`)}
export const GetCommandListApi = (data)=>{return request.post("/command/search",data)}
export const GetIdApi = (username)=>{return request.get(`/users/getId/${username}`)}

export const DeleteElementApi = (data)=>{return request.delete('/events/delete',data)}
export const DeleteContractUserApi = (data)=>{return request.delete('/contractUser/delete',data)}
export const DeleteMachinesApi = (data)=>{return request.delete('/contractMachine/delete',data)}

export const EditElementApi = (data)=>{return request.post('/events/searchOne',data)}

export const UpdateElementApi = (data)=>{return request.put('/events/update',data)}

export const AddElementApi = (Element)=>{return request.post('/events/add',Element)}
export const AddContractUserApi = (data)=>{return request.post('/contractUser/add',data)}
export const AddMachineApi = (data)=>{return request.post('/contractMachine/add',data)}