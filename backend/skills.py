"""
加载和管理 Skill 文件。
Skill 文件格式：带 YAML frontmatter 的 Markdown 文件。
"""
import os
import re
from pathlib import Path
from typing import Optional

SKILLS_DIR = Path(__file__).parent.parent / "skills"


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """解析 YAML frontmatter，返回 (meta, body)。"""
    match = re.match(r"^---\n(.*?)\n---\n(.*)", content, re.DOTALL)
    if not match:
        return {}, content

    meta_block = match.group(1)
    body = match.group(2).strip()

    meta: dict = {}
    # 简单解析：只提取 name 和 description（不引入 PyYAML 依赖）
    for line in meta_block.splitlines():
        if line.startswith("name:"):
            meta["name"] = line.split(":", 1)[1].strip()
        elif line.startswith("description:") and "description" not in meta:
            # description 可能是多行，取第一行非空值
            val = line.split(":", 1)[1].strip()
            if val and val != "|":
                meta["description"] = val

    # 多行 description（以 | 开头的块）
    if "description" not in meta:
        desc_lines = []
        in_desc = False
        for line in meta_block.splitlines():
            if line.startswith("description:"):
                in_desc = True
                continue
            if in_desc:
                if line.startswith(" ") or line.startswith("\t"):
                    desc_lines.append(line.strip())
                else:
                    break
        if desc_lines:
            meta["description"] = " ".join(desc_lines)

    return meta, body


def list_skills() -> list[dict]:
    """列出所有可用的 skills，返回 [{id, name, description}]。"""
    skills = []
    if not SKILLS_DIR.exists():
        return skills

    for path in SKILLS_DIR.glob("*.md"):
        content = path.read_text(encoding="utf-8")
        meta, _ = _parse_frontmatter(content)
        skill_id = path.stem
        # name 可能含换行，取第一个非空行
        raw_name = meta.get("name", skill_id)
        name = next((l.strip() for l in raw_name.splitlines() if l.strip()), skill_id)
        skills.append({
            "id": skill_id,
            "name": name,
            "description": meta.get("description", ""),
        })

    return skills


def get_skill_prompt(skill_id: str) -> Optional[str]:
    """根据 skill_id 获取 system prompt（即 frontmatter 之后的正文）。"""
    path = SKILLS_DIR / f"{skill_id}.md"
    if not path.exists():
        return None
    content = path.read_text(encoding="utf-8")
    _, body = _parse_frontmatter(content)
    return body
