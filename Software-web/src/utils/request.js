import axios from "axios";
import { ElMessage } from "element-plus";
import router from "../router";
import { getApiBaseUrl } from "./systemConfig";

const request = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json;charset=utf-8'  // 设置默认请求头
    },
    timeout: 60000
})

request.interceptors.request.use(
    (config)=>{
        config.baseURL = getApiBaseUrl()
        let loginUser = null
        try {
            loginUser = JSON.parse(localStorage.getItem('loginUserObject'))
        } catch {
            loginUser = null
        }
        if(loginUser && loginUser.token){
            config.headers.token = loginUser.token
        }
        return config
    },
    (error)=>{
        return Promise.reject(error)
    }
)

request.interceptors.response.use(
    (response)=>{
        return response.data
    },
    (error)=>{
        if(error.response && error.response.status === 401){
            localStorage.removeItem('loginUserObject')
            localStorage.removeItem('Id')
            ElMessage.error("登陆超时，请先登录");
            router.push('/login')
        }
        return Promise.reject(error)
    }
);

export default request
