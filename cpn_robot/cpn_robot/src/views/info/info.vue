<script setup>
    import {ref} from 'vue'
    let show = ref(false)
    let info = ref('歪比歪比，歪比巴卜。rua哇rou！')

    function Element(){
        show.value=true;
        info.value='事件提醒：<br><br>应用场景：通过在小程序或网页中添加事件，让机器人在指定时间为用户进行语音提示，避免用户遗忘事件，可起到记事本或闹钟的作用<br><br>使用方法：在网页端“事件管理”或微信小程序“事件”中，查看已设置的事件，并对其进行管理，如新增事件或删除事件等操作<br><br>注意事项：<br>事件名称--在小程序和网页中显示<br>事件优先级--当同一时间有多个事件需要提醒，将按照优先级从高到低依次提醒，因此不建议在同一时间设置大于3个事件<br>事件描述--机器人实际触发语音向用户提醒的内容<br>绑定设备--设备号为?????，需要把事件绑定给一个设备（即机器人）才能生效<br><br>您可在“命令查询”中，查看事件是否被成功触发'
    }
    function Agent(){
        show.value=true;
        info.value='AI陪聊：'
    }
    function Safe(){
        show.value=true;
        info.value='安全监测内容'
    }
    function Video(){
        show.value=true;
        info.value='远程通话内容'
    }
    function Drive(){
        show.value=true;
        info.value='远程遥控内容'
    }
    function no(){
        show.value=true;
        info.value='敬请期待'
    }

</script>

<template>
    <div id="info_container">
        <li class="list" @click="Element">事件提醒</li>
        <li class="list" @click="Agent">智能陪聊</li>
        <li class="list" @click="Safe">安全监测</li>
        <li class="list" @click="Video">远程通话</li>
        <li class="list" @click="Drive">远程遥控</li>
        <li class="list" @click="no">暂未添加</li>
    </div>
    <div id="infomation" v-if="show" v-html="info"></div>
</template>

<style>
    #info_container{
        padding: 10px 25px;
        width: 255px;
        height: 1130px;
        display: flex;
        flex-direction: column;
        background-color: rgb(197, 196, 196);
    }
    #infomation{
        height: 1130px;
        width: 850px;
        background-color: rgb(255, 255, 255);
        position: absolute;
        top: 20px;
        left: 300px;
        padding: 15px;
        font-size: 23px;
    }
    .list{
        height: 80px;
        width: 200px;
        padding: 15px 45px;
        margin: 10px 0;
        background-color: rgb(160, 160, 160);
        display: flex;
        justify-content: left;
        text-align: center;
        align-items: center;
        font-size: 25px;
        border: 3px solid rgb(152, 152, 152);
        border-radius: 7px;
        font-weight: 600;
        color: white;
    }
</style>