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
let SET = ref(true);

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
    const set = SET.value;
    const gets = false;
    const del = false;
    const workflow_id = '7598072302836482048';
    const parameters = {
        username,
        content,
        style,
        time,
        set,
        gets,
        del
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
    const set = SET.value;
    const gets = true;
    const del = false;
    const workflow_id = '7598072302836482048';
    const parameters = {
        username,
        content,
        style,
        time,
        set,
        gets,
        del
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
        const set = SET.value;
        const gets = false;
        const del = false;
        const workflow_id = '7598072302836482048';
        const parameters = {
            username,
            content,
            style,
            time: currentTime,
            set,
            gets,
            del
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

// 清空聊天
function clearChat() {
    chatMessages.value = []
}

// 删除测试记录
const deleteData = async()=> {
  if(confirm('确定删除测试记录？')){
    const username = userName.value;
    const content = Content.value.trim();
    const style = '';
    const set = SET.value;
    const gets = false;
    const del = true;
    const workflow_id = '7598072302836482048';
    const parameters = {
        username,
        content,
        style,
        time: currentTime,
        set,
        gets,
        del
    };
    const data = {
        workflow_id,
        parameters
    }
    const result = await SetStyleOnCozeApi(data)
    if (result.status === 200){
        alert("删除成功");
        clearChat();
    }
    else{
        alert("删除失败");
    }

  }
}

function clear() {
    Content.value = '';
    Style.value = '';
}
</script>

<template>
    <div class="agent_container1">

        <!-- 左侧：人设设置 -->
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

        <!-- 中间：聊天窗口 -->
        <div class="chat_window">
            <div id="Agent_title2">聊天调试窗口</div>
            <div id="chat_input">
                <div id="B">聊天窗口</div>
                <div id="chat">
                    <div class="message-item"
                        :class="{ 'user-message': item.type === 'user', 'ai-message': item.type === 'ai' }"
                        v-for="(item, index) in chatMessages" :key="index">
                        <div class="avatar">
                            {{ item.type === 'user' ? '我' : 'AI' }}
                        </div>
                        <div class="message-bubble">
                            <div class="message-content">{{ item.content }}</div>
                            <div class="message-time">{{ item.time }}</div>
                        </div>
                    </div>
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

        <!-- 右侧：功能按钮 → 与聊天窗口平级！并排！等高！ -->
        <div class="chat_control_bar">
            <button class="control_btn" @click="clearChat">清屏</button>
            清理所有聊天记录的显示
            <button class="control_btn red" @click="deleteData">删除测试记录</button>
            删除已存储在云端数据库中所有用于调试的聊天记录并清屏，不影响正常使用
        </div>

    </div>
</template>

<style>
/* ===== 整体布局 ===== */
.agent_container1 {
  background: linear-gradient(135deg, #FFF8F3, #FFEFE6);
  width: 100%;
  height: 100%;
  display: flex;
  gap: 16px;
  padding: 16px;
  box-sizing: border-box;
  overflow: hidden;
}

/* ===== 左侧 & 中间 卡片统一 ===== */
.style_set,
.chat_window {
  background: #FFFFFF;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(255, 138, 101, 0.08);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 14px;
  box-sizing: border-box;
  overflow: hidden;
}

.style_set {
  width: 32%;
}

.chat_window {
  width: 56%;
}

/* ===== 右侧控制栏 ===== */
.chat_control_bar {
  width: 12%;
  background: #FFFFFF;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 18px;
  box-shadow: 0 8px 24px rgba(255, 138, 101, 0.08);
  font-size: 13px;
  color: #666;
  line-height: 1.6;
}

/* 控制按钮 */
.control_btn {
  width: 100%;
  height: 40px;
  font-size: 14px;
  font-weight: 600;
  border: none;
  border-radius: 10px;
  background: linear-gradient(90deg, #FF8A65, #FF7043);
  color: #fff;
  cursor: pointer;
  margin-bottom: 10px;
  transition: 0.25s;
}

.control_btn:hover {
  transform: scale(1.05);
}

.control_btn.red {
  background: linear-gradient(90deg, #E57373, #D32F2F);
}

/* ===== 标题统一 ===== */
#Agent_title1,
#Agent_title2 {
  height: 60px;
  width: 100%;
  background: linear-gradient(90deg, #FFB199, #FF8A65);
  border-radius: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 22px;
  font-weight: 600;
  color: white;
  margin-bottom: 10px;
}

/* ===== 内容区域 ===== */
#style_input,
#chat_input {
  height: calc(100% - 70px);
  width: 100%;
  background: #FFF7F3;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  padding: 10px;
  box-sizing: border-box;
}

/* 标题文字 */
#A,
#B {
  height: 30px;
  color: #E64A19;
  font-size: 15px;
  font-weight: 600;
}

#B {
  text-align: center;
}

#C {
  color: #999;
  font-size: 12px;
  margin-top: 5px;
}

/* ===== 输入框统一 ===== */
#AI_style,
#chat_info {
  border: 1px solid #FFD6C8;
  border-radius: 10px;
  padding: 10px;
  background-color: #fff;
  outline-color: #FF8A65;
}

#AI_style {
  flex: 1;
  resize: none;
}

#chat_info {
  height: 70px;
  flex: 1;
}

/* ===== 按钮（人设区） ===== */
.set {
  width: 110px;
  height: 34px;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: 0.25s;
}

/* 主按钮 */
.set:not(#get) {
  background: linear-gradient(90deg, #FF8A65, #FF7043);
  color: white;
}

.set:not(#get):hover {
  transform: scale(1.05);
}

/* 获取按钮 */
#get {
  background: #FFE0D6;
  color: #E64A19;
}

#get:hover {
  background: #FFD0C0;
}

/* ===== 聊天输入区 ===== */
.chat_container2 {
  height: 90px;
  width: 100%;
  background: #FFF7F3;
  border-radius: 12px;
  display: flex;
  gap: 10px;
  padding: 10px;
  box-sizing: border-box;
}

/* 发送按钮 */
#send {
  width: 70px;
  height: 60%;
  background: linear-gradient(90deg, #FF8A65, #FF7043);
  color: white;
  font-weight: 600;
  border-radius: 10px;
  border: none;
  cursor: pointer;
}

#send:hover {
  transform: scale(1.05);
}

#send:disabled {
  background: #ccc;
}

/* ===== 聊天框 ===== */
#chat {
  flex: 1;
  background-color: #ffffff;
  border: 1px solid #FFE0D6;
  border-radius: 12px;
  overflow-y: auto;
  padding: 12px;
}

/* 空状态 */
.empty-tip {
  color: #bbb;
  text-align: center;
  margin-top: 30%;
}

/* ===== 聊天气泡 ===== */
.message-item {
  display: flex;
  margin-bottom: 14px;
  max-width: 80%;
}

/* 用户 */
.user-message {
  flex-direction: row-reverse;
  margin-left: auto;
}

/* AI */
.ai-message {
  flex-direction: row;
  margin-right: auto;
}

/* 头像 */
.avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #FF8A65;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 8px;
}

/* 气泡 */
.message-bubble {
  background: #FFF3EE;
  border-radius: 14px;
  padding: 10px 14px;
  line-height: 1.5;
}

.user-message .message-bubble {
  background: #FFDCC8;
}

/* 时间 */
.message-time {
  font-size: 11px;
  color: #999;
  margin-top: 4px;
}

/* 滚动条隐藏 */
#chat::-webkit-scrollbar {
  width: 0;
}
</style>