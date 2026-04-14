<template>
  <div class="message" :class="message.role">
    <div class="avatar">{{ message.role === 'user' ? '你' : '峰' }}</div>
    <div class="bubble">
      <!-- 流式输出中显示纯文本，完成后渲染 Markdown -->
      <div
        v-if="message.role === 'assistant'"
        class="content"
        v-html="renderedContent"
      />
      <div v-else class="content plain">{{ message.content }}</div>
      <span v-if="message.streaming" class="cursor" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  message: Object, // { role, content, streaming? }
})

const renderedContent = computed(() => {
  return marked.parse(props.message.content || '', { breaks: true })
})
</script>

<style scoped>
.message {
  display: flex;
  gap: 12px;
  max-width: 820px;
  margin: 0 auto;
  width: 100%;
  padding: 4px 0;
}

.message.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--surface2);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
  color: var(--primary);
}

.message.user .avatar {
  background: var(--user-bubble);
  color: #7bb8f5;
}

.bubble {
  max-width: calc(100% - 52px);
  padding: 12px 16px;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  background: var(--assistant-bubble);
  line-height: 1.7;
  font-size: 15px;
  position: relative;
}

.message.user .bubble {
  background: var(--user-bubble);
  border-color: #2a4a6f;
}

.content :deep(p) { margin: 0 0 8px; }
.content :deep(p:last-child) { margin-bottom: 0; }
.content :deep(ul), .content :deep(ol) { padding-left: 20px; margin: 6px 0; }
.content :deep(li) { margin: 3px 0; }
.content :deep(strong) { color: var(--primary); font-weight: 600; }
.content :deep(code) {
  background: var(--surface2);
  padding: 1px 5px;
  border-radius: 4px;
  font-size: 13px;
  font-family: 'JetBrains Mono', monospace;
}
.content :deep(blockquote) {
  border-left: 3px solid var(--primary);
  padding-left: 12px;
  margin: 8px 0;
  color: var(--text-muted);
}
.content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
  font-size: 14px;
}
.content :deep(th), .content :deep(td) {
  border: 1px solid var(--border);
  padding: 6px 10px;
}
.content :deep(th) { background: var(--surface2); }

.content.plain { white-space: pre-wrap; word-break: break-word; }

.cursor {
  display: inline-block;
  width: 2px;
  height: 1em;
  background: var(--primary);
  margin-left: 2px;
  vertical-align: text-bottom;
  animation: blink 0.8s step-end infinite;
}
@keyframes blink { 50% { opacity: 0; } }
</style>
