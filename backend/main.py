"""
FastAPI 后端：将 Claude Skills 暴露为流式聊天 API。

端点：
  GET  /api/skills          → 列出所有可用 skills
  POST /api/chat            → 流式聊天（SSE）
  GET  /api/health          → 健康检查
"""
import json
import os
from typing import AsyncIterator

from openai import AsyncOpenAI
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from skills import get_skill_prompt, list_skills

load_dotenv()

app = FastAPI(title="Skills Chat API", version="1.0.0")

# CORS：允许本地 Vue 开发服务器访问；部署时改为实际域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AsyncOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
MODEL = "qwen-plus"


# ── 数据模型 ──────────────────────────────────────────────────────────────────

class Message(BaseModel):
    role: str        # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    skill_id: str
    messages: list[Message]   # 完整的对话历史（前端维护）


# ── 端点 ──────────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/skills")
def skills_list():
    """列出所有可用 skills。"""
    return {"skills": list_skills()}


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """
    流式聊天端点（Server-Sent Events）。
    前端传入完整对话历史 + skill_id，后端注入 system prompt 后调用 Claude。
    """
    system_prompt = get_skill_prompt(req.skill_id)
    if system_prompt is None:
        raise HTTPException(status_code=404, detail=f"Skill '{req.skill_id}' not found")

    messages = [{"role": m.role, "content": m.content} for m in req.messages]

    async def event_stream() -> AsyncIterator[dict]:
        try:
            stream = await client.chat.completions.create(
                model=MODEL,
                max_tokens=4096,
                messages=[{"role": "system", "content": system_prompt}] + messages,
                stream=True,
            )
            async for chunk in stream:
                text_chunk = chunk.choices[0].delta.content or ""
                if text_chunk:
                    yield {
                        "event": "delta",
                        "data": json.dumps({"text": text_chunk}, ensure_ascii=False),
                    }
            yield {"event": "done", "data": json.dumps({"text": ""})}
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)}, ensure_ascii=False),
            }

    return EventSourceResponse(event_stream())
