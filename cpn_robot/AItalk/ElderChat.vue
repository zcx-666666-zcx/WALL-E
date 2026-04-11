<template>
  <div class="elder-ai-app" :class="{ 'large-font': largeFontMode }">
    
    <!-- 顶部栏 -->
    <header class="top-bar">
      <div class="persona-info">
        <div class="avatar" :style="{ background: currentPersona.color }">
          {{ currentPersona.avatar }}
        </div>
        <div class="persona-text">
          <span class="persona-name">{{ currentPersona.name }}</span>
          <span class="persona-status">● 在线陪伴中</span>
        </div>
      </div>
      <div class="top-actions">
        <button class="icon-btn" @click="toggleFontSize" title="切换字体大小">
          {{ largeFontMode ? '🔡' : '🔠' }}
        </button>
        <button class="icon-btn" @click="showPersonaPanel = true" title="切换人设">
          👥
        </button>
        <button class="icon-btn" @click="clearChat" title="清空对话">
          🗑️
        </button>
      </div>
    </header>

    <!-- 聊天区域 -->
    <main class="chat-area" ref="chatArea">
      <!-- 欢迎语 -->
      <div v-if="messages.length === 0" class="welcome-screen">
        <div class="welcome-avatar">{{ currentPersona.avatar }}</div>
        <h2>{{ currentPersona.greeting }}</h2>
        <p>点击下方输入框，开始聊天吧</p>
        <div class="quick-topics">
          <button 
            v-for="topic in quickTopics" 
            :key="topic"
            @click="sendQuickMessage(topic)"
            class="topic-chip"
          >
            {{ topic }}
          </button>
        </div>
      </div>

      <!-- 消息列表 -->
      <div v-for="(msg, index) in messages" :key="index" 
           class="message-wrapper"
           :class="msg.role">
        
        <div v-if="msg.role === 'assistant'" class="ai-avatar">
          {{ currentPersona.avatar }}
        </div>
        
        <div class="message-bubble" :class="msg.role">
          <span class="message-text">{{ msg.content }}</span>
          <span v-if="msg.isStreaming" class="cursor-blink">|</span>
          <div class="message-time">{{ msg.time }}</div>
        </div>
      </div>

      <!-- AI 思考中 -->
      <div v-if="isThinking" class="message-wrapper assistant">
        <div class="ai-avatar">{{ currentPersona.avatar }}</div>
        <div class="message-bubble assistant thinking">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>
    </main>

    <!-- 情感状态提示 -->
    <div v-if="emotionHint" class="emotion-hint">
      {{ emotionHint }}
    </div>

    <!-- 输入区域 -->
    <footer class="input-area">
      <div class="input-wrapper">
        <textarea
          ref="inputBox"
          v-model="inputText"
          :placeholder="currentPersona.inputHint"
          rows="1"
          @keydown.enter.exact.prevent="sendMessage"
          @input="autoResize"
          :disabled="isThinking"
        ></textarea>
        <button 
          class="send-btn"
          @click="sendMessage"
          :disabled="!inputText.trim() || isThinking"
        >
          发送
        </button>
      </div>
      <div class="input-hint">按 Enter 发送 · Shift+Enter 换行</div>
    </footer>

    <!-- 人设选择面板 -->
    <div v-if="showPersonaPanel" class="persona-panel-overlay" @click.self="showPersonaPanel = false">
      <div class="persona-panel">
        <h3>选择陪护伙伴</h3>
        <div class="persona-grid">
          <div 
            v-for="persona in personas" 
            :key="persona.id"
            class="persona-card"
            :class="{ active: currentPersonaId === persona.id }"
            @click="switchPersona(persona.id)"
          >
            <div class="card-avatar" :style="{ background: persona.color }">
              {{ persona.avatar }}
            </div>
            <div class="card-name">{{ persona.name }}</div>
            <div class="card-desc">{{ persona.personality }}</div>
          </div>
        </div>
        <button class="close-btn" @click="showPersonaPanel = false">关闭</button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'

// ===== 配置 =====
const API_BASE = 'http://localhost:8000'
const USER_ID = 'user_' + Math.random().toString(36).slice(2, 8)

// ===== 人设数据 =====
const personas = ref([
  {
    id: 'grandma_chen',
    name: '陈奶奶',
    avatar: '👵',
    color: 'linear-gradient(135deg, #f093fb, #f5576c)',
    personality: '温柔慈祥，爱关心人',
    greeting: '哎哟，你来啦！陈奶奶等你好久了～',
    inputHint: '跟陈奶奶说说话吧...',
    topics: ['聊聊天', '说说心情', '今天吃什么']
  },
  {
    id: 'grandpa_li',
    name: '李大爷',
    avatar: '👴',
    color: 'linear-gradient(135deg, #4facfe, #00f2fe)',
    personality: '爽朗幽默，爱聊时事',
    greeting: '哈哈，来了！今天感觉咋样？',
    inputHint: '跟李大爷聊两句...',
    topics: ['聊新闻', '说笑话', '下棋故事']
  }
])

// ===== 状态 =====
const currentPersonaId = ref('grandma_chen')
const messages = ref([])
const inputText = ref('')
const isThinking = ref(false)
const largeFontMode = ref(false)
const showPersonaPanel = ref(false)
const emotionHint = ref('')
const chatArea = ref(null)
const inputBox = ref(null)

// WebSocket
let ws = null

// ===== 计算属性 =====
const currentPersona = computed(() => 
  personas.value.find(p => p.id === currentPersonaId.value) || personas.value[0]
)

const quickTopics = computed(() => currentPersona.value.topics || [])

// ===== 方法 =====
function connectWebSocket() {
  ws = new WebSocket(`${API_BASE.replace('http', 'ws')}/ws/${USER_ID}`)
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    
    if (data.type === 'chunk') {
      // 流式追加内容
      const lastMsg = messages.value[messages.value.length - 1]
      if (lastMsg && lastMsg.role === 'assistant' && lastMsg.isStreaming) {
        lastMsg.content += data.content
        scrollToBottom()
      }
    } else if (data.type === 'done') {
      // 完成
      const lastMsg = messages.value[messages.value.length - 1]
      if (lastMsg) lastMsg.isStreaming = false
      isThinking.value = false
    }
  }
  
  ws.onclose = () => {
    setTimeout(connectWebSocket, 3000) // 断线重连
  }
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || isThinking.value) return
  
  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: text,
    time: getCurrentTime(),
    isStreaming: false
  })
  
  inputText.value = ''
  isThinking.value = true
  scrollToBottom()
  
  // 使用 SSE 流式接口（备用方案，WebSocket 不可用时）
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    await sendViaSSE(text)
    return
  }
  
  // 准备 AI 回复气泡
  await nextTick()
  isThinking.value = false
  messages.value.push({
    role: 'assistant',
    content: '',
    time: getCurrentTime(),
    isStreaming: true
  })
  
  // 通过 WebSocket 发送
  ws.send(JSON.stringify({
    text,
    persona_id: currentPersonaId.value
  }))
}

async function sendViaSSE(text) {
  const response = await fetch(`${API_BASE}/api/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: USER_ID,
      message: text,
      persona_id: currentPersonaId.value
    })
  })
  
  messages.value.push({
    role: 'assistant',
    content: '',
    time: getCurrentTime(),
    isStreaming: true
  })
  isThinking.value = false
  
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    
    const text = decoder.decode(value)
    const lines = text.split('\n')
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const payload = line.slice(6)
        if (payload === '[DONE]') {
          const lastMsg = messages.value[messages.value.length - 1]
          if (lastMsg) lastMsg.isStreaming = false
          break
        }
        try {
          const data = JSON.parse(payload)
          const lastMsg = messages.value[messages.value.length - 1]
          if (lastMsg?.isStreaming) {
            lastMsg.content += data.chunk
            scrollToBottom()
          }
        } catch (e) {}
      }
    }
  }
}

function sendQuickMessage(topic) {
  inputText.value = topic
  sendMessage()
}

function switchPersona(personaId) {
  currentPersonaId.value = personaId
  showPersonaPanel.value = false
  messages.value = []  // 切换人设时清空对话
}

function clearChat() {
  if (confirm('确定要清空对话吗？')) {
    messages.value = []
    fetch(`${API_BASE}/api/chat/clear`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: USER_ID })
    })
  }
}

function toggleFontSize() {
  largeFontMode.value = !largeFontMode.value
  localStorage.setItem('largeFontMode', largeFontMode.value)
}

function scrollToBottom() {
  nextTick(() => {
    if (chatArea.value) {
      chatArea.value.scrollTop = chatArea.value.scrollHeight
    }
  })
}

function getCurrentTime() {
  return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function autoResize(e) {
  const el = e.target
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 120) + 'px'
}

// ===== 生命周期 =====
onMounted(() => {
  largeFontMode.value = localStorage.getItem('largeFontMode') === 'true'
  connectWebSocket()
})

onUnmounted(() => {
  if (ws) ws.close()
})
</script>

<style scoped>
/* ===== 全局 ===== */
.elder-ai-app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f1eb;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-size: 16px;
  color: #333;
  max-width: 480px;
  margin: 0 auto;
}

.elder-ai-app.large-font {
  font-size: 20px;
}

/* ===== 顶部栏 ===== */
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: white;
  border-bottom: 1px solid #eee;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.persona-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

.persona-name {
  display: block;
  font-weight: 600;
  font-size: 1em;
}

.persona-status {
  font-size: 0.75em;
  color: #4caf50;
}

.top-actions {
  display: flex;
  gap: 8px;
}

.icon-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  transition: background 0.2s;
}

.icon-btn:hover { background: #f0f0f0; }

/* ===== 聊天区域 ===== */
.chat-area {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* ===== 欢迎屏 ===== */
.welcome-screen {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.welcome-avatar {
  font-size: 64px;
  margin-bottom: 16px;
}

.welcome-screen h2 {
  font-size: 1.1em;
  color: #333;
  margin-bottom: 8px;
}

.quick-topics {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  margin-top: 20px;
}

.topic-chip {
  padding: 8px 16px;
  background: white;
  border: 1.5px solid #e8a87c;
  color: #c96a2a;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9em;
  transition: all 0.2s;
}

.topic-chip:hover {
  background: #e8a87c;
  color: white;
}

/* ===== 消息 ===== */
.message-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 8px;
}

.message-wrapper.user {
  flex-direction: row-reverse;
}

.ai-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f093fb, #f5576c);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.message-bubble {
  max-width: 72%;
  padding: 10px 14px;
  border-radius: 18px;
  line-height: 1.6;
  position: relative;
}

.message-bubble.user {
  background: #e8a87c;
  color: white;
  border-bottom-right-radius: 4px;
}

.message-bubble.assistant {
  background: white;
  color: #333;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.message-time {
  font-size: 0.65em;
  color: rgba(0,0,0,0.3);
  margin-top: 4px;
  text-align: right;
}

.user .message-time { color: rgba(255,255,255,0.7); }

/* 光标闪烁 */
.cursor-blink {
  animation: blink 0.8s infinite;
  color: #e8a87c;
}
@keyframes blink { 0%, 100% { opacity: 1 } 50% { opacity: 0 } }

/* 思考动画 */
.thinking {
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 14px 18px;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ccc;
  animation: bounce 1.2s infinite;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%, 100% { transform: translateY(0) } 50% { transform: translateY(-6px); background: #e8a87c; } }

/* ===== 情感提示 ===== */
.emotion-hint {
  text-align: center;
  font-size: 0.8em;
  color: #888;
  padding: 4px;
  background: #fff8f0;
  border-top: 1px solid #f0e0cc;
}

/* ===== 输入区 ===== */
.input-area {
  background: white;
  border-top: 1px solid #eee;
  padding: 10px 16px 16px;
}

.input-wrapper {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

textarea {
  flex: 1;
  border: 1.5px solid #ddd;
  border-radius: 20px;
  padding: 10px 16px;
  font-size: 1em;
  font-family: inherit;
  resize: none;
  outline: none;
  line-height: 1.5;
  transition: border-color 0.2s;
  max-height: 120px;
}

textarea:focus { border-color: #e8a87c; }

.send-btn {
  background: linear-gradient(135deg, #e8a87c, #c96a2a);
  color: white;
  border: none;
  border-radius: 20px;
  padding: 10px 20px;
  font-size: 1em;
  cursor: pointer;
  white-space: nowrap;
  transition: opacity 0.2s;
}

.send-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.send-btn:not(:disabled):hover { opacity: 0.9; }

.input-hint {
  font-size: 0.72em;
  color: #bbb;
  text-align: center;
  margin-top: 4px;
}

/* ===== 人设面板 ===== */
.persona-panel-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: flex-end;
  z-index: 100;
}

.persona-panel {
  background: white;
  width: 100%;
  border-radius: 20px 20px 0 0;
  padding: 24px 16px;
  max-height: 70vh;
  overflow-y: auto;
}

.persona-panel h3 {
  text-align: center;
  margin-bottom: 20px;
  font-size: 1.1em;
}

.persona-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 20px;
}

.persona-card {
  border: 2px solid #eee;
  border-radius: 16px;
  padding: 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.persona-card.active {
  border-color: #e8a87c;
  background: #fff8f0;
}

.card-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  margin: 0 auto 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
}

.card-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.card-desc {
  font-size: 0.8em;
  color: #888;
}

.close-btn {
  width: 100%;
  padding: 12px;
  background: #f5f1eb;
  border: none;
  border-radius: 12px;
  font-size: 1em;
  cursor: pointer;
}
</style>
