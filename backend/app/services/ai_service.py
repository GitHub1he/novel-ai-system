from openai import OpenAI
from app.core.config import settings
from typing import List, Dict, Optional
import json


class AIService:
    def __init__(self):
        self.client = None
        # 支持智谱AI和OpenAI兼容接口
        api_key = settings.ZHIPUAI_API_KEY or settings.OPENAI_API_KEY
        if api_key:
            self.client = OpenAI(
                api_key=api_key,
                base_url=settings.OPENAI_API_BASE
            )

    def _build_context(self, project_data: dict, characters: list, world_settings: list) -> str:
        """构建AI生成的上下文"""
        context_parts = []

        # 项目基础信息
        if project_data:
            context_parts.append(f"## 小说信息\n")
            context_parts.append(f"书名：{project_data.get('title', '')}\n")
            context_parts.append(f"类型：{project_data.get('genre', '')}\n")
            context_parts.append(f"简介：{project_data.get('summary', '')}\n")
            context_parts.append(f"文风：{project_data.get('style', '通俗')}\n\n")

        # 人物信息
        if characters:
            context_parts.append(f"## 人物设定\n")
            for char in characters[:5]:  # 限制人物数量
                context_parts.append(f"- {char.get('name')}：{char.get('personality', '')}\n")
            context_parts.append("\n")

        # 世界观设定
        if world_settings:
            context_parts.append(f"## 世界观设定\n")
            for setting in world_settings[:3]:  # 限制设定数量
                context_parts.append(f"- {setting.get('name')}：{setting.get('description', '')}\n")
            context_parts.append("\n")

        return "".join(context_parts)

    def generate_chapter(
        self,
        prompt: str,
        context: str,
        word_count: int = 2000,
        style: Optional[str] = None
    ) -> str:
        """生成章节内容"""
        if not self.client:
            raise ValueError("AI服务未配置，请设置OPENAI_API_KEY")

        system_prompt = f"""你是一个专业的小说创作助手。根据以下设定和用户要求，创作小说内容。

{context}

创作要求：
1. 字数约{word_count}字
2. 保持人物性格一致
3. 遵守世界观设定
4. {f'文风：{style}' if style else ''}
"""

        try:
            response = self.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=word_count * 2
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"AI生成失败: {str(e)}")

    def generate_outline(
        self,
        project_info: dict,
        chapter_count: int = 10
    ) -> List[Dict]:
        """生成大纲"""
        if not self.client:
            raise ValueError("AI服务未配置，请设置OPENAI_API_KEY")

        prompt = f"""为一本{project_info.get('genre', '')}小说生成{chapter_count}章的大纲。
书名：《{project_info.get('title', '')}》
简介：{project_info.get('summary', '')}

请生成每章的标题和简要情节描述，以JSON格式返回。"""

        try:
            response = self.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            result = response.choices[0].message.content
            return json.loads(result).get("chapters", [])
        except Exception as e:
            raise Exception(f"大纲生成失败: {str(e)}")

    def expand_content(self, content: str, target_words: int = 3000) -> str:
        """扩写内容"""
        if not self.client:
            raise ValueError("AI服务未配置，请设置OPENAI_API_KEY")

        prompt = f"""请将以下内容扩写到{target_words}字左右，保持原有的情节和人物性格不变：

{content}"""

        try:
            response = self.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=target_words * 2
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"扩写失败: {str(e)}")


# 全局AI服务实例
ai_service = AIService()
