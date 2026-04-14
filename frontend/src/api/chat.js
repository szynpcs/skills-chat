/**
 * 调用后端 SSE 流式聊天接口。
 *
 * @param {string} skillId
 * @param {Array<{role: string, content: string}>} messages
 * @param {(delta: string) => void} onDelta  - 每次收到文字片段时的回调
 * @param {() => void} onDone               - 流结束时的回调
 * @param {(err: string) => void} onError    - 出错时的回调
 * @returns {() => void}  调用后返回一个 abort 函数，可用于取消请求
 */
export function streamChat(skillId, messages, onDelta, onDone, onError) {
  const controller = new AbortController()

  fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ skill_id: skillId, messages }),
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok) {
        const text = await res.text()
        onError(`HTTP ${res.status}: ${text}`)
        return
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          if (line.startsWith('event: delta')) continue
          if (line.startsWith('event: done')) {
            onDone()
            return
          }
          if (line.startsWith('event: error')) continue
          if (line.startsWith('data: ')) {
            try {
              const payload = JSON.parse(line.slice(6))
              if (payload.text !== undefined) onDelta(payload.text)
              if (payload.message) onError(payload.message)
            } catch {
              // 忽略解析错误
            }
          }
        }
      }
      onDone()
    })
    .catch((err) => {
      if (err.name !== 'AbortError') onError(err.message)
    })

  return () => controller.abort()
}

export async function fetchSkills() {
  const res = await fetch('/api/skills')
  const data = await res.json()
  return data.skills
}
