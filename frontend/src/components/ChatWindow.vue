<template>
  <div class="chat-window">
    <!-- 消息列表 -->
    <div class="messages" ref="messagesEl">
      <!-- 空状态 -->
      <div v-if="messages.length === 0" class="empty-state">
        <div class="empty-icon">💬</div>
        <p>选择一个角色，开始对话</p>
      </div>

      <MessageBubble
        v-for="(msg, i) in messages"
        :key="i"
        :message="msg"
      />
    </div>

    <!-- 输入区 -->
    <div class="input-area">
      <textarea
        ref="inputEl"
        v-model="inputText"
        :placeholder="isStreaming ? '正在生成回答...' : '输入消息，Enter 发送，Shift+Enter 换行'"
        :disabled="isStreaming"
        @keydown.enter.exact.prevent="send"
        rows="1"
        @input="autoResize"
      />
      <button
        class="send-btn"
        :disabled="!inputText.trim() || isStreaming"
        @click="send"
      >
        <span v-if="!isStreaming">发送</span>
        <span v-else class="stop-icon" @click.stop="abort">■ 停止</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import MessageBubble from './MessageBubble.vue'
import { streamChat } from '../api/chat.js'

const props = defineProps({
  skillId: String,
})

const messages = ref([])
const inputText = ref('')
const isStreaming = ref(false)
const messagesEl = ref(null)
const inputEl = ref(null)
let abortFn = null

// 切换 skill 时清空对话
watch(() => props.skillId, () => {
  messages.value = []
})

async function send() {
  const text = inputText.value.trim()
  if (!text || isStreaming.value) return

  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  await nextTick()
  resetInputHeight()
  scrollToBottom()

  // 添加助手占位消息
  messages.value.push({ role: 'assistant', content: '', streaming: true })
  isStreaming.value = true
  const assistantIdx = messages.value.length - 1

  const history = messages.value
    .slice(0, -1) // 排除还空的助手消息
    .map(m => ({ role: m.role, content: m.content }))

  abortFn = streamChat(
    props.skillId,
    history,
    (delta) => {
      messages.value[assistantIdx].content += delta
      scrollToBottom()
    },
    () => {
      messages.value[assistantIdx].streaming = false
      isStreaming.value = false
      abortFn = null
    },
    (err) => {
      messages.value[assistantIdx].content += `\n\n⚠️ 错误：${err}`
      messages.value[assistantIdx].streaming = false
      isStreaming.value = false
      abortFn = null
    },
  )
}

function abort() {
  if (abortFn) {
    abortFn()
    const last = messages.value[messages.value.length - 1]
    if (last?.streaming) last.streaming = false
    isStreaming.value = false
    abortFn = null
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesEl.value) {
      messagesEl.value.scrollTop = messagesEl.value.scrollHeight
    }
  })
}

function autoResize() {
  const el = inputEl.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 160) + 'px'
}

function resetInputHeight() {
  if (inputEl.value) inputEl.value.style.height = 'auto'
}
</script>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  height: 100%;
  color: var(--text-muted);
}
.empty-icon { font-size: 48px; }
.empty-state p { font-size: 15px; }

.input-area {
  display: flex;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid var(--border);
  background: var(--surface);
  align-items: flex-end;
}

textarea {
  flex: 1;
  background: var(--surface2);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 10px 14px;
  border-radius: var(--radius);
  font-size: 15px;
  font-family: inherit;
  resize: none;
  outline: none;
  line-height: 1.5;
  transition: border-color 0.2s;
  max-height: 160px;
  overflow-y: auto;
}
textarea:focus { border-color: var(--primary); }
textarea:disabled { opacity: 0.5; cursor: not-allowed; }
textarea::placeholder { color: var(--text-muted); }

.send-btn {
  background: var(--primary);
  color: #000;
  border: none;
  padding: 10px 20px;
  border-radius: var(--radius);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, opacity 0.2s;
  white-space: nowrap;
  height: 42px;
}
.send-btn:hover:not(:disabled) { background: var(--primary-dark); }
.send-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.stop-icon { color: #000; font-weight: 600; }
</style>
