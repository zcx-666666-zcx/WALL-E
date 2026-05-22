<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { GetNameApi } from '../../api/users';
import { toast, confirm as toastConfirm } from '../../utils/toast';

// ── 后端地址（本地 FastAPI）──────────────────
const API_BASE = 'http://117.50.44.170:6006';

// ── 状态 ────────────────────────────────────
let userName      = ref('');
const Content     = ref('');
const Style       = ref('');
const GET         = ref('获取当前人设');
const SEND        = ref('发送');
const SUBMIT      = ref('提交人设');
const chatMessages= ref([]);
const chatContainer = ref(null);
let userId = ref(localStorage.getItem('Id'));

// 每个用户只有自己的瓦利，persona_id = wali_{username}
const currentPersonaId = ref('');

// 右侧面板信息
const backendStatus = ref('检测中…');

// ── 初始化 ──────────────────────────────────
onMounted(async () => {
  await getname();           // 先拿到 userName
  currentPersonaId.value = `wali_${userName.value}`;  // 固定为自己的瓦利
  await checkBackend();
});

// ── 获取用户名 ───────────────────────────────
const getname = async () => {
  const id = userId.value;
  const result = await GetNameApi(id);
  if (result && result.code === 1) {
    if (result.data) {
      userName.value = result.data.username;
      return;
    }
    toast.error('获取用户名失败');
  }
};

// ── 工具：滚到底部 ───────────────────────────
const scrollToBottom = async () => {
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

// ── 工具：当前时间字符串 ──────────────────────
function nowStr() {
  return new Date().toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit'
  });
}

// ════════════════════════════════════════════
// 后端状态检测
// ════════════════════════════════════════════
const checkBackend = async () => {
  try {
    const res = await fetch(`${API_BASE}/health`);
    const data = await res.json();
    backendStatus.value = data.status === 'ok' ? '● 在线' : '● 异常';
  } catch {
    backendStatus.value = '● 离线';
  }
};

// ════════════════════════════════════════════
// 人设相关
// ════════════════════════════════════════════

// 获取当前用户的瓦利人设内容，展示在左侧文本框
const getStyle = async () => {
  GET.value = '获取中…';
  try {
    const res = await fetch(`${API_BASE}/personas/${currentPersonaId.value}`);
    if (!res.ok) throw new Error();  
    const data = await res.json();
    Style.value = data.persona_desc || data.personality || '暂无人设描述';
  } catch {
    toast.error('获取失败，请确认后端服务已启动');
  } finally {
    GET.value = '获取当前人设';
  }
};

// 提交人设：更新当前用户的瓦利，不新建
const sendStyle = async () => {
  if (!Style.value.trim()) { toast.warning('请先填写人设描述'); return; }
  SUBMIT.value = '提交中…';
  try {
    const res = await fetch(`${API_BASE}/personas/${currentPersonaId.value}`, {
      method:  'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        persona_desc: Style.value
      }),
    });

    if (!res.ok) throw new Error((await res.json()).detail || '提交失败');
    toast.success('人设已更新成功');
    Style.value = '';
  } catch (e) {
    toast.error('提交失败：' + e.message);
  } finally {
    SUBMIT.value = '提交人设';
  }
};

// ════════════════════════════════════════════
// 聊天
// ════════════════════════════════════════════

const sendMessage = async () => {
  if (!Content.value.trim()) { toast.warning('请输入信息'); return; }
  SEND.value = '发送中';

  const userText = Content.value.trim();
  const time     = nowStr();

  chatMessages.value.push({ type: 'user', content: userText, time });
  Content.value = '';
  scrollToBottom();

  // 先插入一条空的 AI 消息，用于流式追加
  chatMessages.value.push({ type: 'ai', content: '', time, streaming: true });
  scrollToBottom();

  try {
    // 不传 persona_id，后端自动用该用户绑定的瓦利
    const res = await fetch(`${API_BASE}/chat/stream`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userName.value,   // 用 username 作为 user_id
        message: userText,
      }),
    });

    if (!res.ok) throw new Error('请求失败');

    const reader  = res.body.getReader();
    const decoder = new TextDecoder();
    const lastMsg = chatMessages.value[chatMessages.value.length - 1];

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const text  = decoder.decode(value);
      const lines = text.split('\n');
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const payload = line.slice(6).trim();
        if (payload === '[DONE]') break;
        try {
          const obj = JSON.parse(payload);
          if (obj.chunk !== undefined) {
            lastMsg.content += obj.chunk;
            scrollToBottom();
          }
        } catch { /* 忽略非 JSON 行 */ }
      }
    }
    lastMsg.streaming = false;

  } catch (err) {
    const lastMsg = chatMessages.value[chatMessages.value.length - 1];
    lastMsg.content   = '发送失败：' + err.message;
    lastMsg.streaming = false;
  } finally {
    SEND.value = '发送';
  }
};

// ════════════════════════════════════════════
// 操作面板
// ════════════════════════════════════════════

// 清屏（仅前端）
function clearChat() {
  chatMessages.value = [];
}

// 清空后端对话历史
const deleteData = async () => {
  if (!await toastConfirm('确定清除服务端对话历史记录？此操作不可撤销。')) return;
  try {
    await fetch(`${API_BASE}/chat/clear`, {   // 去掉多余的 /api 前缀
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ user_id: userName.value }),
    });
    clearChat();
    toast.success('删除成功');
  } catch {
    toast.error('删除失败，请确认后端服务已启动');
  }
};
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
        <span>瓦利人设设置</span>
      </div>

      <div class="panel-body">

        <!-- 当前人设身份提示 -->
        <div class="persona-badge">
          <span class="persona-avatar">🤖</span>
          <div>
            <div class="persona-name">瓦利</div>
            <div class="persona-id">{{ currentPersonaId || '加载中…' }}</div>
          </div>
        </div>

        <div class="field-label">
          <span class="label-dot"></span>
          人设描述 / 自定义风格
        </div>
        <textarea
          class="styled-textarea"
          v-model="Style"
          placeholder="描述瓦利的性格和说话风格。&#10;&#10;例：活泼开朗，感情细腻，说话简练，不以疑问句结尾，遇到烦心事会很热情。&#10;&#10;点击「获取当前人设」可查看现有配置，修改后点「提交人设」保存。"
        ></textarea>

        <div class="btn-row">
          <button class="btn-primary" @click="sendStyle">{{ SUBMIT }}</button>
          <button class="btn-ghost"   @click="getStyle">{{ GET }}</button>
        </div>

        <div class="tip-box">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="flex-shrink:0;margin-top:1px">
            <circle cx="7" cy="7" r="6" stroke="#E07050" stroke-width="1.2"/>
            <path d="M7 6v4M7 4.5v.5" stroke="#E07050" stroke-width="1.3" stroke-linecap="round"/>
          </svg>
          提交后会直接更新你的瓦利，建议先获取当前版本再修改。
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
          <div class="empty-sub">在下方输入消息，开始调试瓦利的人设吧</div>
        </div>
        <div
          v-for="(item, index) in chatMessages"
          :key="index"
          class="msg-row"
          :class="item.type === 'user' ? 'msg-user' : 'msg-ai'"
        >
          <div class="msg-avatar" :class="item.type === 'user' ? 'avatar-user' : 'avatar-ai'">
            {{ item.type === 'user' ? '我' : '瓦' }}
          </div>
          <div class="msg-body">
            <div class="msg-bubble" :class="item.type === 'user' ? 'bubble-user' : 'bubble-ai'">
              <template v-if="item.type === 'ai' && item.streaming && !item.content">
                <span class="typing-dots"><span></span><span></span><span></span></span>
              </template>
              <template v-else>
                {{ item.content }}<span v-if="item.streaming" class="cursor-blink">▋</span>
              </template>
            </div>
            <div class="msg-time">{{ item.time }}</div>
          </div>
        </div>
      </div>

      <div class="chat-input-area">
        <textarea
          class="chat-textarea"
          v-model="Content"
          placeholder="输入消息，测试瓦利的人设效果…"
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
          <p class="ctrl-desc">清除当前页面所有聊天记录的显示，不影响服务端数据</p>
        </div>

        <div class="control-divider"></div>

        <div class="control-item">
          <button class="ctrl-btn ctrl-red" @click="deleteData">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="flex-shrink:0">
              <path d="M7 1a6 6 0 100 12A6 6 0 007 1zM5 7h4" stroke="white" stroke-width="1.3" stroke-linecap="round"/>
            </svg>
            删除测试记录
          </button>
          <p class="ctrl-desc">清除服务端该用户的对话历史并清屏，长期记忆不受影响</p>
        </div>

        <div class="control-divider"></div>

        <div class="control-info">
          <div class="info-row">
            <span class="info-label">当前用户</span>
            <span class="info-value">{{ userName || '加载中…' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">专属人设</span>
            <span class="info-value">瓦利</span>
          </div>
          <div class="info-row">
            <span class="info-label">消息条数</span>
            <span class="info-value">{{ chatMessages.length }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">后端状态</span>
            <span class="info-value" :style="backendStatus.includes('在线') ? 'color:#4CAF50' : 'color:#E57373'">
              {{ backendStatus }}
            </span>
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

/* 人设身份卡片 */
.persona-badge {
  display: flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, #FFF4EE, #FFE8DA);
  border: 1px solid rgba(255,160,120,0.25);
  border-radius: 12px;
  padding: 10px 14px;
}
.persona-avatar {
  font-size: 26px;
  line-height: 1;
}
.persona-name {
  font-size: 14px;
  font-weight: 700;
  color: #5A3020;
}
.persona-id {
  font-size: 11px;
  color: #C4A898;
  margin-top: 2px;
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
  animation: msgIn 0.35s ease both;
}
@keyframes msgIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
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

/* 流式光标 */
.cursor-blink {
  display: inline-block;
  animation: cur 0.8s step-end infinite;
  color: #FF8A65;
  font-size: 12px;
}
@keyframes cur { 0%,100%{opacity:1} 50%{opacity:0} }

/* 等待输入指示器 */
.typing-dots {
  display: flex; gap: 5px; align-items: center; padding: 2px 0;
}
.typing-dots span {
  width: 7px; height: 7px; border-radius: 50%;
  background: #D0B8A8;
  animation: dotBounce 1.4s ease infinite;
}
.typing-dots span:nth-child(1) { animation-delay: 0s; }
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes dotBounce {
  0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
  40% { transform: translateY(-6px); opacity: 1; }
}

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

@media (max-width: 900px) {
  .agent-root { flex-direction: column; overflow-y: auto; }
  .panel-style, .panel-chat, .panel-control { width: 100%; flex: none; }
  .panel-chat { height: 400px; }
  .panel-style { height: auto; }
  .panel-control { height: auto; }
}
</style>