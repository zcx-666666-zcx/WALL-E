<script setup>
    import{ref} from 'vue';
    import {RegisApi} from '@/api/users.js';
    import { ElMessage } from 'element-plus';
    import { useRouter } from 'vue-router';
    
    const router = useRouter()
    let log = ref("注册")
    let username = ref('');
    let password = ref('');
    let sure_password = ref('');
    let phoneNumber = ref('');

    const GoToLogin = ()=>{
        router.push({
            path: '/login'
        })
    }

    const regis = async()=>{
        log.value="注册中...";
        if(!username.value || !password.value){
            alert("请输入完整内容");
            log.value="注册";
            return;
        }
        if(password.value!=sure_password.value){
            alert("密码不一致");
            log.value="注册";
            return;
        }
        else{
            const RegisInfo = {username: username.value,phoneNumber: phoneNumber.value,password: password.value}
            const result = await RegisApi(RegisInfo);
            if(result.code){
                log.value="注册";
                alert("注册成功");
                GoToLogin();
            }
            else{
                ElMessage.error(result.msg);
                alert("注册失败")
                log.value="注册";
            }
        }
    }
</script>

<template>
    <div class="container">
        <div id="form">
            <p>注册账号</p>
            <input v-model="username" type="text" id="Uinput" placeholder="用户名：">
            <input v-model="password" type="password" class="Pinput" placeholder="密码:">
            <input v-model="sure_password" type="password" class="Pinput" placeholder="确认密码:">
            <input v-model="phoneNumber" type="text" class="Pinput" placeholder="手机号码:">
            <button @click="regis">{{log}}</button>
            <p id="regis" @click="GoToLogin">已有账号？点击登录</p>
        </div>
    </div>
</template>

<style>
    #regis{
        font-size: 120%;
        color: rgb(112, 16, 16);
    }
    #regis:hover{
        color: rgb(180, 16, 16);
    }
    .container{
        height: 100vh;
        width: 100vw;
        background-color: rgb(121, 121, 121);
        display: flex;
        justify-content: center;
        align-items: center;
    }
    p{
        margin: 0 0 40px 0;
        font-size: 550%;
        font-weight: 700;
    }  
    #form{
        height: 65%;
        width: 65%;
        background-image: url("http://localhost:8080/images/index_picture.png");
        position: absolute;
        background-size: cover;
        border: 4px solid rgb(73, 73, 73);
        border-radius: 10px;
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
    }
    #Uinput{
        height: 5%;
        width: 20%;
        font-size: 100%;
        font-weight: 700;
        margin: 0 0 10px 0;
        padding: 10px;
        background-color: rgb(166, 255, 255);
        opacity: 0.7;
    }
    .Pinput{
        height: 5%;
        width: 20%;
        font-size: 100%;
        font-weight: 700;
        margin: 10px 0;
        padding: 10px;
        background-color: rgb(166, 255, 255);
        opacity: 0.7;
    }
    button{
        margin: 15px;
        height: 4%;
        width: 5%;
        background-color: rgb(255, 255, 255);
        opacity: 0.9;
    }
</style>