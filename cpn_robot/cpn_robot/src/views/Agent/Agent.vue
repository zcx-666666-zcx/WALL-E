<script setup>
import { ref, onMounted } from 'vue';
import { GetNameApi } from '../../api/users';
import { SetStyleOnCozeApi } from '../../api/users';

let userid = ref(localStorage.getItem('Id'));
let userName = ref('');
let Content = ref('');
let Style = ref('');
let GET = ref('获取当前人设');
let SEND = ref('发送');
let SUBMIT = ref('提交');
let chatMessages = ref([]);

onMounted(() => {
    getname();
});

const getname = async () => {
    const id = userid.value;
    const result = await GetNameApi(id);
    if (result && result.code === 1) {
        if (result.data) {
            userName.value = result.data.username;
            console.log(userName.value);
            return;
        }
        alert("获取用户名失败");
        return;
    }
}

const sendStyle = async () => {
    SUBMIT.value = '提交中';
    const username = userName.value;
    const content = Content.value;
    const style = Style.value;
    const time = new Date();
    const workflow_id = '7598072302836482048';
    const parameters = {
        username,
        content,
        style,
        time
    };
    const data = {
        workflow_id,
        parameters
    }

    const result = await SetStyleOnCozeApi(data)
    console.log(result);
    if (result.status === 200) {
        SUBMIT.value = '提交';
        clear();
        alert("设置成功");
    } else {
        SUBMIT.value = '提交';
        alert("设置失败");
    }
}

const getStyle = async () => {
    GET.value = '获取中...'
    const username = userName.value;
    const content = '';
    const style = '';
    const time = new Date();
    const workflow_id = '7598072302836482048';
    const parameters = {
        username,
        content,
        style,
        time
    };
    const data = {
        workflow_id,
        parameters
    }
    const result = await SetStyleOnCozeApi(data)
    if (result.status === 200) {
        if (result.data) {
            let extractedStyle = '';
            const sseData = result.data;
            const messageBlocks = sseData.split('\n\n').filter(block => block.trim());
            for (const block of messageBlocks) {
                const dataLine = block.split('\n').find(line => line.trim().startsWith('data:'));
                if (!dataLine) continue;
                const dataObj = JSON.parse(dataLine.replace('data:', '').trim());
                if (dataObj.content) {
                    const contentObj = JSON.parse(dataObj.content);
                    if (contentObj.style) {
                        extractedStyle = contentObj.style;
                        GET.value = '获取当前人设';
                        break;
                    }
                }
            }
            if (extractedStyle) {
                Style.value = extractedStyle;
                GET.value = '获取当前人设';
            }
        } else {
            GET.value = '获取当前人设';
            alert("获取失败");
        }

    } else {
        GET.value = '获取当前人设';
        alert("获取失败");
    }
}

const sendMessage = async () => {
    SEND.value = '发送中';
    try {
        if (!Content.value.trim()) {
            alert("请输入信息");
            return;
        }
        const currentTime = new Date();
        const timeStr = currentTime.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });

        const userMessage = {
            type: 'user',
            content: Content.value.trim(),
            time: timeStr
        };
        chatMessages.value.push(userMessage);

        const username = userName.value;
        const content = Content.value.trim();
        const style = '';
        const workflow_id = '7598072302836482048';
        const parameters = {
            username,
            content,
            style,
            time: currentTime
        };
        const data = {
            workflow_id,
            parameters
        }

        const result = await SetStyleOnCozeApi(data);
        console.log("接口返回：", result.data);

        let aiReply = '暂无回复';
        if (result && result.status === 200 && result.data) {
            const sseData = result.data;
            const messageBlocks = sseData.split('\n\n').filter(block => block.trim());

            for (const block of messageBlocks) {
                const dataLine = block.split('\n').find(line => line.trim().startsWith('data:'));
                if (!dataLine) continue;

                let dataObj = {};
                try {
                    dataObj = JSON.parse(dataLine.replace('data:', '').trim());
                } catch (e) {
                    console.error("解析data失败：", e);
                    continue;
                }

                if (dataObj.content) {
                    let contentObj = {};
                    try {
                        contentObj = JSON.parse(dataObj.content);
                    } catch (e) {
                        console.error("解析content失败：", e);
                        continue;
                    }
                    if (contentObj.contentOutput) {
                        aiReply = contentObj.contentOutput;
                        console.log("AI回复：", aiReply);
                        break;
                    }
                }
            }
        }
        const aiMessage = {
            type: 'ai',
            content: aiReply,
            time: timeStr
        };
        chatMessages.value.push(aiMessage);
        clear();

    } catch (error) {
        console.error("发送消息失败：", error);
        alert("发送失败：" + error.message);
    } finally {
        SEND.value = '发送';
    }
}

function clear() {
    Content.value = '';
    Style.value = '';
}
</script>

<template>
    <div class="agent_container1">
        <div class="style_set">
            <div id="Agent_title1">AI人设设置</div>
            <div id="style_input">
                <div id="A">请输入AI人设:</div>
                <textarea name="style" id="AI_style" v-model="Style"
                    placeholder="请在此输入你希望呈现的AI人设，或者聊天风格。例如：用户是男性，年龄为70岁，你是一名女性，年龄为75岁。你平时待人和善，乐于助人，每次说完话喜欢询问对方意见。系统默认风格为”大模型自适应“。支持自然语言描述与markdown格式"></textarea>
                <div id="style_send">
                    <button class="set" @click="sendStyle">{{SUBMIT}}</button>
                    <button class="set" id="get" @click="getStyle">{{ GET }}</button>
                </div>
            </div>
            <div class="style_container2">
                提示：若未获取当前人设且直接提交AI人设，会覆盖之前的人设版本。建议先获取当前人设后再在其基础上进行编辑
            </div>
        </div>
        <div class="chat_window">
            <div id="Agent_title2">聊天调试窗口</div>
            <div id="chat_input">
                <div id="B">聊天窗口</div>
                <div id="chat">
                    <div class="message-item"
                        :class="{ 'user-message': item.type === 'user', 'ai-message': item.type === 'ai' }"
                        v-for="(item, index) in chatMessages" :key="index">
                        <!-- 头像占位 -->
                        <div class="avatar">
                            {{ item.type === 'user' ? '我' : 'AI' }}
                        </div>
                        <!-- 消息内容气泡 -->
                        <div class="message-bubble">
                            <div class="message-content">{{ item.content }}</div>
                            <div class="message-time">{{ item.time }}</div>
                        </div>
                    </div>
                    <!-- 空状态提示 -->
                    <div v-if="chatMessages.length === 0" class="empty-tip">
                        暂无聊天记录，输入消息开始对话吧～
                    </div>
                </div>
                <div id="C">注：请文明用语，避免因违规言语造成不必要的麻烦</div>
            </div>
            <div class="chat_container2">
                <textarea name="chat" id="chat_info" v-model="Content" placeholder="请输入信息"></textarea>
                <button id="send" @click="sendMessage" :disabled="SEND === '发送中'">{{ SEND }}</button>
            </div>
        </div>
    </div>
</template>

<style>
#get{
    background-color: rgb(145, 190, 134);
}
#chat_info {
    height: 80px;
    width: calc(100% - 80px);
    flex: 1;
}
#send {
    height: 80px;
    width: 60px;
    background-color: rgb(18, 221, 18);
    color: white;
    font-weight: 600;
    font-size: 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    flex-shrink: 0;
}
#send:disabled 
{
    background-color: #cccccc;
    cursor: not-allowed;
}
#chat {
    width: 100%;
    height: calc(100% - 60px);
    background-color: white;
    border: 1px solid rgb(179, 179, 179);
    overflow-y: auto;
    padding: 10px;
    box-sizing: border-box;
}
.empty-tip {
    color: #999;
    font-size: 16px;
    text-align: center;
    margin-top: 40%;
}
.message-item {
    display: flex;
    margin-bottom: 15px;
    max-width: 80%;
}
.user-message {
    flex-direction: row-reverse;
    margin-left: auto;
}
.ai-message {
    flex-direction: row;
    margin-right: auto;
}
.avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: #e0e0e0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: bold;
    margin: 0 10px;
    flex-shrink: 0;
}
.message-bubble {
    color: black;
    background-color: #f0f0f0;
    border-radius: 10px;
    padding: 8px 12px;
    text-align: left;
    word-wrap: break-word;
    white-space: pre-wrap;
}
.user-message .message-bubble {
    background-color: #d3eafd;
}
.message-time {
    font-size: 12px;
    color: #999;
    margin-top: 5px;
}
.agent_container1 {
    background-color: aliceblue;
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: flex-start;
    align-items: stretch;
    gap: 10px;
    padding: 0 10px;
    box-sizing: border-box;
    overflow: hidden;
}
.style_set {
    background-color: white;
    height: 100%;
    width: 35%;
    max-width: 600px;
    min-width: 300px;
    border-radius: 5px;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 10px;
    box-sizing: border-box;
    overflow: hidden;
}
.chat_window {
    background-color: white;
    height: 100%;
    width: 65%;
    max-width: 800px;
    min-width: 400px;
    border-radius: 5px;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 10px;
    box-sizing: border-box;
    overflow: hidden;
}
#Agent_title1 {
    margin: 0 0 10px 0;
    height: 70px;
    width: 100%;
    background-color: rgb(226, 226, 226);
    border-radius: 5px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: clamp(18px, 2vw, 33px);
    font-weight: 600;
    color: rgb(44, 44, 44);
    flex-shrink: 0;
}
#Agent_title2 {
    margin: 0 0 10px 0;
    height: 70px;
    width: 100%;
    background-color: rgb(226, 226, 226);
    border-radius: 5px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: clamp(18px, 2vw, 33px);
    font-weight: 600;
    color: rgb(44, 44, 44);
    flex-shrink: 0;
}
#style_input {
    height: calc(100% - 80px);
    width: 100%;
    background-color: rgb(226, 226, 226);
    border-radius: 5px;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 5px;
    box-sizing: border-box;
    overflow: hidden;
}
#chat_input {
    height: calc(100% - 140px);
    width: 100%;
    background-color: rgb(226, 226, 226);
    border-radius: 5px;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 5px;
    box-sizing: border-box;
    overflow: hidden;
}
#A {
    height: 35px;
    width: 100%;
    padding: 0 5px;
    color: black;
    font-size: clamp(14px, 1.5vw, 20px);
    text-align: left;
    flex-shrink: 0;
}
#B {
    height: 35px;
    width: 100%;
    padding: 0 5px;
    color: black;
    font-size: clamp(14px, 1.5vw, 20px);
    text-align: center;
    flex-shrink: 0;
}
#C {
    margin: 6px 0 0 0;
    height: 20px;
    width: 100%;
    padding: 0 5px;
    color: black;
    font-size: clamp(12px, 1vw, 15px);
    text-align: left;
    flex-shrink: 0;
}
#AI_style {
    height: calc(100% - 85px);
    width: 100%;
    font-size: clamp(12px, 1.2vw, 17px);
    resize: none;
    box-sizing: border-box;
}
.style_container2 {
    display: none;
}
.chat_container2 {
    margin: 10px 0 0 0;
    height: 100px;
    width: 100%;
    background-color: rgb(226, 226, 226);
    border-radius: 5px;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 10px;
    padding: 0 10px;
    box-sizing: border-box;
    flex-shrink: 0;
}
#style_send {
    margin: 10px 0 0 0;
    height: 40px;
    width: 100%;
    display: flex;
    justify-content: flex-start;
    align-items: center;
    flex-shrink: 0;
}
.set {
    width: 120px;
    height: 30px;
    margin: 0 10px 0 0;
    flex-shrink: 0;
}
#chat::-webkit-scrollbar {
    width: 0px;
    height: 0px;
}
#chat::-webkit-scrollbar-track {
    background: transparent;
}
#chat::-webkit-scrollbar-thumb {
    background: transparent;
}
</style>