import axios from "axios";
import { ElMessage } from "element-plus";
import router from "../router";
import { getApiBaseUrl } from "./systemConfig";
import { clearAuthSession, isManualLogoutInProgress } from "./authSession";

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
        const path = String(config.url || '')
        const isPublicAuthPath = path.includes('/login') || path.includes('/users/register') || path.includes('/system-config/public')
        let loginUser = null
        try {
            loginUser = JSON.parse(localStorage.getItem('loginUserObject'))
        } catch {
            loginUser = null
        }
        if(loginUser && loginUser.token){
            config.headers.token = loginUser.token
        } else if (!isPublicAuthPath) {
            const error = new axios.Cancel('auth session missing')
            error.code = 'AUTH_SESSION_MISSING'
            error.__authSilent = true
            throw error
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
        if(error.__authSilent || error.code === 'AUTH_SESSION_MISSING'){
            return Promise.reject(error)
        }
        if(error.response && error.response.status === 401){
            const manualLogout = isManualLogoutInProgress()
            clearAuthSession()
            if (!manualLogout && router.currentRoute.value.path !== '/login') {
                ElMessage.error("登录超时，请先登录");
            }
            if (router.currentRoute.value.path !== '/login') {
                router.replace('/login')
            }
        }
        return Promise.reject(error)
    }
);

export default request
