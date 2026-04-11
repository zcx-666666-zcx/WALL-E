<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { GetNameApi } from '../../api/users';
import { SetStyleOnCozeApi } from '../../api/users';

let userid = ref(localStorage.getItem('Id'));
let userName = ref('');
let Content = ref('');
let Style = ref('');
let GET = ref('获取当前人设');
let SEND = ref('发送');
let SUBMIT = ref('提交人设');
let chatMessages = ref([]);
let SET = ref(true);
let chatContainer = ref(null);

onMounted(() => {
    getname();
});

const scrollToBottom = async () => {
    await nextTick();
    if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
    }
};

const getname = async () => {
    const id = userid.value;
    const result = await GetNameApi(id);
    if (result && result.code === 1) {
        if (result.data) {
            userName.value = result.data.username;
            return;
        }
        alert("获取用户名失败");
    }
}

const sendStyle = async () => {
    SUBMIT.value = '提交中…';
    const username = userName.value;
    const content = Content.value;
    const style = Style.value;
    const time = new Date();
    const result = await SetStyleOnCozeApi({
        workflow_id: '7598072302836482048',
        parameters: { username, content, style, time, set: true, gets: false, del: false }
    });
    SUBMIT.value = '提交人设';
    if (result.status === 200) { clear(); alert("设置成功"); }
    else alert("设置失败");
}

const getStyle = async () => {
    GET.value = '获取中…';
    const username = userName.value;
    const result = await SetStyleOnCozeApi({
        workflow_id: '7598072302836482048',
        parameters: { username, content: '', style: '', time: new Date(), set: true, gets: true, del: false }
    });
    GET.value = '获取当前人设';
    if (result.status === 200 && result.data) {
        let extractedStyle = '';
        const messageBlocks = result.data.split('\n\n').filter(b => b.trim());
        for (const block of messageBlocks) {
            const dataLine = block.split('\n').find(l => l.trim().startsWith('data:'));
            if (!dataLine) continue;
            try {
                const dataObj = JSON.parse(dataLine.replace('data:', '').trim());
                if (dataObj.content) {
                    const contentObj = JSON.parse(dataObj.content);
                    if (contentObj.style) { extractedStyle = contentObj.style; break; }
                }
            } catch (e) { continue; }
        }
        if (extractedStyle) Style.value = extractedStyle;
        else alert("获取失败");
    } else alert("获取失败");
}

const sendMessage = async () => {
    if (!Content.value.trim()) { alert("请输入信息"); return; }
    SEND.value = '发送中';
    try {
        const currentTime = new Date();
        const timeStr = currentTime.toLocaleString('zh-CN', {
            year: 'numeric', month: '2-digit', day: '2-digit',
            hour: '2-digit', minute: '2-digit', second: '2-digit'
        });
        chatMessages.value.push({ type: 'user', content: Content.value.trim(), time: timeStr });
        scrollToBottom();

        const result = await SetStyleOnCozeApi({
            workflow_id: '7598072302836482048',
            parameters: { username: userName.value, content: Content.value.trim(), style: '', time: currentTime, set: true, gets: false, del: false }
        });

        let aiReply = '暂无回复';
        if (result && result.status === 200 && result.data) {
            const messageBlocks = result.data.split('\n\n').filter(b => b.trim());
            for (const block of messageBlocks) {
                const dataLine = block.split('\n').find(l => l.trim().startsWith('data:'));
                if (!dataLine) continue;
                try {
                    const dataObj = JSON.parse(dataLine.replace('data:', '').trim());
                    if (dataObj.content) {
                        const contentObj = JSON.parse(dataObj.content);
                        if (contentObj.contentOutput) { aiReply = contentObj.contentOutput; break; }
                    }
                } catch (e) { continue; }
            }
        }
        chatMessages.value.push({ type: 'ai', content: aiReply, time: timeStr });
        clear();
        scrollToBottom();
    } catch (error) {
        alert("发送失败：" + error.message);
    } finally {
        SEND.value = '发送';
    }
}

function clearChat() { chatMessages.value = []; }

const deleteData = async () => {
    if (confirm('确定删除云端所有测试记录？此操作不可撤销。')) {
        const result = await SetStyleOnCozeApi({
            workflow_id: '7598072302836482048',
            parameters: { username: userName.value, content: '', style: '', time: new Date(), set: SET.value, gets: false, del: true }
        });
        if (result.status === 200) { alert("删除成功"); clearChat(); }
        else alert("删除失败");
    }
}

function clear() { Content.value = ''; Style.value = ''; }
</script>

<template>
  <div class="agent-root">

    <!-- ══ 左侧：人设设置 ══ -->
    <div class="panel panel-style">
      <div class="panel-header">
        <div class="panel-header-icon">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <circle cx="8" cy="5" r="3" stroke="white" stroke-width="1.5"/>
            <path d="M2 13c0-3 2.5-5 6-5s6 2 6 5" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </div>
        <span>AI 人设设置</span>
      </div>

      <div class="panel-body">
        <div class="field-label">
          <span class="label-dot"></span>
          当前人设描述
        </div>
        <textarea
          class="styled-textarea"
          v-model="Style"
          placeholder="请描述 AI 的人设与聊天风格。&#10;&#10;例：用户是男性，70 岁。AI 是一位75 岁的温和女性，乐于助人，每次发言后会询问对方感受。&#10;&#10;若首次使用，请先点击「获取当前人设」再编辑。支持自然语言或 Markdown 格式。"
        ></textarea>

        <div class="btn-row">
          <button class="btn-primary" @click="sendStyle">{{ SUBMIT }}</button>
          <button class="btn-ghost" @click="getStyle">{{ GET }}</button>
        </div>

        <div class="tip-box">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="flex-shrink:0;margin-top:1px">
            <circle cx="7" cy="7" r="6" stroke="#E07050" stroke-width="1.2"/>
            <path d="M7 6v4M7 4.5v.5" stroke="#E07050" stroke-width="1.3" stroke-linecap="round"/>
          </svg>
          直接提交会覆盖旧人设。建议先获取当前版本，再在此基础上修改。
        </div>
      </div>
    </div>

    <!-- ══ 中间：聊天调试 ══ -->
    <div class="panel panel-chat">
      <div class="panel-header">
        <div class="panel-header-icon">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M2 3a1 1 0 011-1h10a1 1 0 011 1v7a1 1 0 01-1 1H9l-3 2v-2H3a1 1 0 01-1-1V3z" stroke="white" stroke-width="1.5" stroke-linejoin="round"/>
          </svg>
        </div>
        <span>聊天调试窗口</span>
        <div class="header-badge">
          <span class="live-dot"></span>
          实时对话
        </div>
      </div>

      <div class="chat-messages" ref="chatContainer">
        <div v-if="chatMessages.length === 0" class="empty-state">
          <div class="empty-icon">💬</div>
          <div class="empty-text">暂无聊天记录</div>
          <div class="empty-sub">在下方输入消息，开始调试 AI 人设吧</div>
        </div>
        <div
          v-for="(item, index) in chatMessages"
          :key="index"
          class="msg-row"
          :class="item.type === 'user' ? 'msg-user' : 'msg-ai'"
        >
          <div class="msg-avatar" :class="item.type === 'user' ? 'avatar-user' : 'avatar-ai'">
            {{ item.type === 'user' ? '我' : 'AI' }}
          </div>
          <div class="msg-body">
            <div class="msg-bubble" :class="item.type === 'user' ? 'bubble-user' : 'bubble-ai'">
              {{ item.content }}
            </div>
            <div class="msg-time">{{ item.time }}</div>
          </div>
        </div>
      </div>

      <div class="chat-input-area">
        <textarea
          class="chat-textarea"
          v-model="Content"
          placeholder="输入消息，测试 AI 人设效果…"
          @keydown.enter.ctrl="sendMessage"
        ></textarea>
        <div class="chat-input-footer">
          <span class="input-hint">Ctrl + Enter 发送</span>
          <button
            class="btn-send"
            @click="sendMessage"
            :disabled="SEND === '发送中'"
          >
            <svg v-if="SEND === '发送'" width="14" height="14" viewBox="0 0 14 14" fill="none" style="margin-right:4px">
              <path d="M1 7l11-5-4 5 4 5L1 7z" fill="white"/>
            </svg>
            {{ SEND }}
          </button>
        </div>
      </div>

      <div class="chat-disclaimer">
        请文明用语，避免因违规内容造成不必要的影响
      </div>
    </div>

    <!-- ══ 右侧：操作面板 ══ -->
    <div class="panel panel-control">
      <div class="panel-header panel-header-sm">
        <div class="panel-header-icon">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <rect x="1" y="1" width="5" height="5" rx="1.2" stroke="white" stroke-width="1.3"/>
            <rect x="8" y="1" width="5" height="5" rx="1.2" stroke="white" stroke-width="1.3"/>
            <rect x="1" y="8" width="5" height="5" rx="1.2" stroke="white" stroke-width="1.3"/>
            <rect x="8" y="8" width="5" height="5" rx="1.2" stroke="white" stroke-width="1.3"/>
          </svg>
        </div>
        <span>操作面板</span>
      </div>

      <div class="control-body">
        <div class="control-item">
          <button class="ctrl-btn ctrl-orange" @click="clearChat">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="flex-shrink:0">
              <path d="M2 4h10M5 4V2.5a.5.5 0 01.5-.5h3a.5.5 0 01.5.5V4M6 7v3M8 7v3M3 4l.7 7.2a.8.8 0 00.8.8h5a.8.8 0 00.8-.8L11 4" stroke="white" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            清屏
          </button>
          <p class="ctrl-desc">清除当前页面所有聊天记录的显示，不影响云端数据</p>
        </div>

        <div class="control-divider"></div>

        <div class="control-item">
          <button class="ctrl-btn ctrl-red" @click="deleteData">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="flex-shrink:0">
              <path d="M7 1a6 6 0 100 12A6 6 0 007 1zM5 7h4" stroke="white" stroke-width="1.3" stroke-linecap="round"/>
            </svg>
            删除测试记录
          </button>
          <p class="ctrl-desc">永久删除云端数据库中的调试聊天记录并清屏，不影响正式使用数据</p>
        </div>

        <div class="control-divider"></div>

        <div class="control-info">
          <div class="info-row">
            <span class="info-label">当前用户</span>
            <span class="info-value">{{ userName || '加载中…' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">消息条数</span>
            <span class="info-value">{{ chatMessages.length }}</span>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* ══ 根容器 ══ */
.agent-root {
  width: 100%;
  height: 100%;
  display: flex;
  gap: 14px;
  box-sizing: border-box;
  overflow: hidden;
  font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}

/* ══ 卡片通用 ══ */
.panel {
  background: #FFFFFF;
  border-radius: 16px;
  border: 1px solid rgba(255, 160, 120, 0.12);
  box-shadow: 0 4px 20px rgba(200, 90, 50, 0.07);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
}

.panel-style  { width: 30%; }
.panel-chat   { width: 54%; }
.panel-control{ width: 16%; }

/* ══ Panel Header ══ */
.panel-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  background: linear-gradient(90deg, #FF9A76, #FF6B40);
  font-size: 15px;
  font-weight: 700;
  color: white;
  letter-spacing: 0.04em;
  flex-shrink: 0;
}
.panel-header-sm { padding: 12px 16px; font-size: 14px; }

.panel-header-icon {
  width: 30px; height: 30px;
  border-radius: 8px;
  background: rgba(255,255,255,0.2);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

.header-badge {
  margin-left: auto;
  display: flex; align-items: center; gap: 5px;
  background: rgba(255,255,255,0.18);
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 100px;
  padding: 3px 10px;
  font-size: 11px; font-weight: 500;
  letter-spacing: 0.03em;
}
.live-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: #A8FFCA;
  box-shadow: 0 0 5px rgba(168,255,202,0.8);
  animation: blink 2s ease infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ══ 人设面板 body ══ */
.panel-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px;
  gap: 12px;
  overflow: hidden;
}

.field-label {
  display: flex; align-items: center; gap: 6px;
  font-size: 13px; font-weight: 600; color: #5A3020;
}
.label-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: linear-gradient(135deg, #FF9A76, #FF6040);
  flex-shrink: 0;
}

.styled-textarea {
  flex: 1;
  resize: none;
  border: 1px solid rgba(255, 160, 120, 0.3);
  border-radius: 12px;
  padding: 12px 14px;
  font-size: 13px;
  line-height: 1.7;
  color: #3A2010;
  background: #FFFAF7;
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s;
}
.styled-textarea:focus { border-color: #FF8A65; background: #FFFFFF; }
.styled-textarea::placeholder { color: #C4A898; }

.btn-row {
  display: flex; gap: 8px;
}
.btn-primary {
  flex: 1; height: 38px;
  background: linear-gradient(90deg, #FF9A76, #FF6040);
  color: white; border: none; border-radius: 10px;
  font-size: 13px; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: all 0.2s ease;
  box-shadow: 0 3px 10px rgba(255,96,64,0.25);
}
.btn-primary:hover { transform: translateY(-1px); box-shadow: 0 5px 14px rgba(255,96,64,0.32); }
.btn-primary:active { transform: translateY(0); }

.btn-ghost {
  flex: 1; height: 38px;
  background: #FFF0E8; color: #E06030;
  border: 1px solid rgba(255,140,100,0.3); border-radius: 10px;
  font-size: 13px; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: all 0.2s ease;
}
.btn-ghost:hover { background: #FFE4D4; border-color: #FF8A65; }

.tip-box {
  display: flex; gap: 7px; align-items: flex-start;
  background: #FFF8F5;
  border: 1px solid rgba(255,140,100,0.2);
  border-left: 3px solid #FF9A76;
  border-radius: 0 8px 8px 0;
  padding: 9px 12px;
  font-size: 12px; color: #8A5040; line-height: 1.6;
}

/* ══ 聊天区 ══ */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  background: #FFFAF7;
  border-top: 1px solid rgba(255,160,120,0.1);
  border-bottom: 1px solid rgba(255,160,120,0.1);
}
.chat-messages::-webkit-scrollbar { width: 4px; }
.chat-messages::-webkit-scrollbar-track { background: transparent; }
.chat-messages::-webkit-scrollbar-thumb { background: rgba(255,160,120,0.3); border-radius: 4px; }

/* 空状态 */
.empty-state {
  flex: 1;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: 6px; padding: 40px 0;
}
.empty-icon { font-size: 32px; filter: grayscale(0.2); }
.empty-text { font-size: 14px; font-weight: 600; color: #B09080; }
.empty-sub  { font-size: 12px; color: #C4B0A8; }

/* 消息行 */
.msg-row {
  display: flex; gap: 10px; align-items: flex-end;
  max-width: 80%;
}
.msg-user { flex-direction: row-reverse; align-self: flex-end; }
.msg-ai   { flex-direction: row; align-self: flex-start; }

.msg-avatar {
  width: 34px; height: 34px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700;
  flex-shrink: 0;
}
.avatar-user { background: linear-gradient(135deg, #FF9A76, #FF6040); color: white; }
.avatar-ai   { background: linear-gradient(135deg, #FFD4B8, #FFBFA0); color: #C05030; }

.msg-body { display: flex; flex-direction: column; gap: 3px; }
.msg-user .msg-body { align-items: flex-end; }
.msg-ai   .msg-body { align-items: flex-start; }

.msg-bubble {
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 13.5px; line-height: 1.65; color: #3A2010;
  word-break: break-word;
}
.bubble-user {
  background: linear-gradient(135deg, #FF9A76, #FF7050);
  color: white;
  border-bottom-right-radius: 4px;
}
.bubble-ai {
  background: white;
  border: 1px solid rgba(255,160,120,0.2);
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(200,90,50,0.06);
}
.msg-time { font-size: 10px; color: #C4B0A8; padding: 0 4px; }

/* 输入区 */
.chat-input-area {
  padding: 12px 16px 8px;
  display: flex; flex-direction: column; gap: 8px;
  flex-shrink: 0;
}
.chat-textarea {
  width: 100%; height: 70px;
  resize: none; border: 1px solid rgba(255,160,120,0.3);
  border-radius: 12px; padding: 10px 14px;
  font-size: 13px; line-height: 1.6; font-family: inherit;
  color: #3A2010; background: #FFFAF7; outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}
.chat-textarea:focus { border-color: #FF8A65; background: white; }
.chat-textarea::placeholder { color: #C4A898; }

.chat-input-footer {
  display: flex; align-items: center; justify-content: space-between;
}
.input-hint { font-size: 11px; color: #C4A898; }

.btn-send {
  display: flex; align-items: center;
  justify-content: center;
  height: 34px; padding: 0 18px;
  width: 15%;
  background: linear-gradient(90deg, #FF9A76, #FF6040);
  color: white; border: none; border-radius: 10px;
  font-size: 13px; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: all 0.2s ease;
  box-shadow: 0 3px 10px rgba(255,96,64,0.25);
}
.btn-send:hover { transform: translateY(-1px); box-shadow: 0 5px 14px rgba(255,96,64,0.32); }
.btn-send:disabled { background: #DDD; box-shadow: none; cursor: not-allowed; transform: none; }

.chat-disclaimer {
  text-align: center;
  font-size: 11px; color: #C4A898;
  padding: 6px 16px 10px;
  flex-shrink: 0;
}

/* ══ 右侧控制面板 ══ */
.control-body {
  flex: 1;
  padding: 16px;
  display: flex; flex-direction: column; gap: 0;
  overflow-y: auto;
}

.control-item {
  display: flex; flex-direction: column; gap: 8px;
  padding: 4px 0 12px;
}

.ctrl-btn {
  width: 80%; height: 38px;
  display: flex; align-items: center; justify-content: center; gap: 6px;
  border: none; border-radius: 10px;
  font-size: 13px; font-weight: 600; font-family: inherit;
  color: white; cursor: pointer;
  transition: all 0.2s ease;
}
.ctrl-orange {
  background: linear-gradient(90deg, #FF9A76, #FF6040);
  box-shadow: 0 3px 10px rgba(255,96,64,0.22);
}
.ctrl-orange:hover { transform: translateY(-1px); box-shadow: 0 5px 14px rgba(255,96,64,0.3); }
.ctrl-red {
  background: linear-gradient(90deg, #E57373, #D32F2F);
  box-shadow: 0 3px 10px rgba(200,50,50,0.18);
}
.ctrl-red:hover { transform: translateY(-1px); box-shadow: 0 5px 14px rgba(200,50,50,0.28); }

.ctrl-desc {
  font-size: 11.5px; color: #A09088; line-height: 1.6; margin: 0;
}

.control-divider {
  height: 1px;
  background: rgba(255,160,120,0.12);
  margin: 4px 0 14px;
}

.control-info {
  background: #FFF8F5;
  border-radius: 10px;
  border: 1px solid rgba(255,160,120,0.15);
  padding: 12px 14px;
  display: flex; flex-direction: column; gap: 8px;
}
.info-row {
  display: flex; justify-content: space-between; align-items: center;
}
.info-label { font-size: 11px; color: #B09080; }
.info-value  { font-size: 13px; font-weight: 600; color: #5A3020; }
</style>