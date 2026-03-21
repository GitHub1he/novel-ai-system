from openai import OpenAI
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.project import Project
from app.models.character import Character
from app.models.world_setting import WorldSetting
from app.models.plot_node import PlotNode
from app.models.chapter import Chapter
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

    def analyze_context_requirements(
        self,
        project_id: int,
        previous_chapter_id: Optional[int] = None,
        plot_direction: Optional[str] = None
    ) -> Dict[str, List]:
        """
        分析上下文需求，AI智能推荐可用的角色、设定和情节节点

        Args:
            project_id: 项目ID
            previous_chapter_id: 前一章ID（可选）
            plot_direction: 情节方向说明（可选）

        Returns:
            Dict包含validated_characters, validated_world_settings, validated_plot_nodes
        """
        if not self.client:
            return {
                "validated_characters": [],
                "validated_world_settings": [],
                "validated_plot_nodes": []
            }

        db = SessionLocal()
        try:
            # 获取项目基础信息
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                return {
                    "validated_characters": [],
                    "validated_world_settings": [],
                    "validated_plot_nodes": []
                }

            # 获取所有相关数据
            characters = db.query(Character).filter(Character.project_id == project_id).all()
            world_settings = db.query(WorldSetting).filter(WorldSetting.project_id == project_id).all()
            plot_nodes = db.query(PlotNode).filter(PlotNode.project_id == project_id).all()

            # 获取前一章的最后800字符
            previous_context = ""
            if previous_chapter_id:
                previous_chapter = db.query(Chapter).filter(Chapter.id == previous_chapter_id).first()
                if previous_chapter and previous_chapter.content:
                    # 取最后800个字符
                    previous_context = previous_chapter.content[-800:].strip()

            # 构建分析提示
            analysis_prompt = self._build_analysis_prompt(
                project=project,
                characters=characters,
                world_settings=world_settings,
                plot_nodes=plot_nodes,
                previous_context=previous_context,
                plot_direction=plot_direction
            )

            # 调用AI进行分析
            try:
                response = self.client.chat.completions.create(
                    model=settings.AI_MODEL,
                    messages=[
                        {"role": "system", "content": """你是一个专业的小说创作助手。请根据项目信息和情节方向，分析并推荐最适合的角色、世界观设定和情节节点。

请严格按照JSON格式返回，包含以下字段：
- suggested_characters: 推荐的角色ID列表（最多10个）
- suggested_world_settings: 推荐的世界观设定ID列表（最多10个）
- suggested_plot_nodes: 推荐的情节节点ID列表（最多10个）

请确保推荐的实体与当前情节方向相符。"""},
                        {"role": "user", "content": analysis_prompt}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )

                # 解析AI响应
                result = response.choices[0].message.content
                ai_recommendations = json.loads(result)

                # 验证并丰富推荐结果
                validated_result = self._validate_and_enrich_recommendations(
                    ai_recommendations,
                    characters,
                    world_settings,
                    plot_nodes
                )

                return validated_result

            except Exception:
                # AI调用失败，返回空数组（降级到手动选择）
                return {
                    "validated_characters": [],
                    "validated_world_settings": [],
                    "validated_plot_nodes": []
                }

        finally:
            db.close()

    def _build_analysis_prompt(
        self,
        project: Project,
        characters: List[Character],
        world_settings: List[WorldSetting],
        plot_nodes: List[PlotNode],
        previous_context: str = "",
        plot_direction: Optional[str] = None
    ) -> str:
        """
        构建AI分析的提示词

        Args:
            project: 项目信息
            characters: 角色列表
            world_settings: 世界观设定列表
            plot_nodes: 情节节点列表
            previous_context: 前文上下文
            plot_direction: 情节方向

        Returns:
            构建好的提示词
        """
        # 构建项目信息
        project_info = {
            "title": project.title,
            "genre": project.genre,
            "summary": project.summary or "",
            "style": project.style or "通俗"
        }

        # 构建角色信息（最多取10个）
        character_info = []
        for char in characters[:10]:
            char_data = {
                "id": char.id,
                "name": char.name,
                "role": char.role.value if char.role else "supporting",
                "personality": char.personality or "",
                "core_motivation": char.core_motivation or ""
            }
            character_info.append(char_data)

        # 构建世界观设定信息（最多取10个）
        setting_info = []
        for setting in world_settings[:10]:
            setting_data = {
                "id": setting.id,
                "name": setting.name,
                "type": setting.setting_type.value if setting.setting_type else "other",
                "description": setting.description or "",
                "is_core_rule": bool(setting.is_core_rule)
            }
            setting_info.append(setting_data)

        # 构建情节节点信息（最多取10个）
        plot_info = []
        for node in plot_nodes[:10]:
            node_data = {
                "id": node.id,
                "title": node.title,
                "type": node.plot_type.value if node.plot_type else "other",
                "importance": node.importance.value if node.importance else "main",
                "description": node.description or ""
            }
            plot_info.append(node_data)

        # 组装提示词
        prompt_parts = [
            f"## 小说项目信息\n",
            f"书名：{project_info['title']}\n",
            f"类型：{project_info['genre']}\n",
            f"简介：{project_info['summary']}\n",
            f"文风：{project_info['style']}\n\n",

            f"## 可用角色（{len(character_info)}个）\n"
        ]

        for char in character_info:
            prompt_parts.append(
                f"- [{char['id']}] {char['name']}（{char['role']}）：{char['personality']}"
            )
            if char['core_motivation']:
                prompt_parts.append(f"，核心动机：{char['core_motivation']}")
            prompt_parts.append("\n")

        prompt_parts.extend([
            f"\n## 世界观设定（{len(setting_info)}个）\n"
        ])

        for setting in setting_info:
            prompt_parts.append(
                f"- [{setting['id']}] {setting['name']}（{setting['type']}）：{setting['description']}"
            )
            if setting['is_core_rule']:
                prompt_parts.append("【核心规则】")
            prompt_parts.append("\n")

        prompt_parts.extend([
            f"\n## 情节节点（{len(plot_info)}个）\n"
        ])

        for node in plot_info:
            prompt_parts.append(
                f"- [{node['id']}] {node['title']}（{node['type']}，{node['importance']}）：{node['description']}\n"
            )

        if previous_context:
            prompt_parts.extend([
                f"\n## 前文上下文（最后800字符）\n",
                f"{previous_context}\n"
            ])

        if plot_direction:
            prompt_parts.extend([
                f"\n## 情节方向\n",
                f"{plot_direction}\n"
            ])

        prompt_parts.extend([
            f"\n请基于以上信息，推荐最适合当前情节发展的角色、世界观设定和情节节点。",
            f"注意："
            f"1. 推荐要符合情节方向",
            f"2. 优先选择核心规则设定",
            f"3. 控制每个类别最多10个推荐",
            f"4. 返回JSON格式的ID列表"
        ])

        return "".join(prompt_parts)

    def _validate_and_enrich_recommendations(
        self,
        ai_recommendations: Dict,
        characters: List[Character],
        world_settings: List[WorldSetting],
        plot_nodes: List[PlotNode]
    ) -> Dict[str, List]:
        """
        验证AI推荐的ID并返回完整的实体信息

        Args:
            ai_recommendations: AI返回的推荐字典
            characters: 所有角色列表
            world_settings: 所有世界观设定列表
            plot_nodes: 所有情节节点列表

        Returns:
            包含完整实体信息的字典
        """
        # 获取AI推荐的ID
        suggested_character_ids = ai_recommendations.get("suggested_characters", [])
        suggested_setting_ids = ai_recommendations.get("suggested_world_settings", [])
        suggested_plot_ids = ai_recommendations.get("suggested_plot_nodes", [])

        # 验证角色ID并获取完整信息
        validated_characters = []
        character_id_map = {char.id: char for char in characters}

        for char_id in suggested_character_ids:
            if char_id in character_id_map:
                char = character_id_map[char_id]
                validated_characters.append({
                    "id": char.id,
                    "name": char.name,
                    "role": char.role.value if char.role else "supporting",
                    "personality": char.personality or "",
                    "core_motivation": char.core_motivation or "",
                    "age": char.age,
                    "gender": char.gender,
                    "appearance": char.appearance or "",
                    "identity": char.identity or ""
                })

        # 验证世界观设定ID并获取完整信息
        validated_settings = []
        setting_id_map = {setting.id: setting for setting in world_settings}

        for setting_id in suggested_setting_ids:
            if setting_id in setting_id_map:
                setting = setting_id_map[setting_id]
                validated_settings.append({
                    "id": setting.id,
                    "name": setting.name,
                    "type": setting.setting_type.value if setting.setting_type else "other",
                    "description": setting.description or "",
                    "attributes": setting.attributes or {},
                    "is_core_rule": bool(setting.is_core_rule)
                })

        # 验证情节节点ID并获取完整信息
        validated_plots = []
        plot_id_map = {node.id: node for node in plot_nodes}

        for plot_id in suggested_plot_ids:
            if plot_id in plot_id_map:
                node = plot_id_map[plot_id]
                validated_plots.append({
                    "id": node.id,
                    "title": node.title,
                    "type": node.plot_type.value if node.plot_type else "other",
                    "importance": node.importance.value if node.importance else "main",
                    "description": node.description or "",
                    "conflict_points": node.conflict_points or "",
                    "theme_tags": node.theme_tags or [],
                    "sequence_number": node.sequence_number
                })

        return {
            "validated_characters": validated_characters,
            "validated_world_settings": validated_settings,
            "validated_plot_nodes": validated_plots
        }


# 全局AI服务实例
ai_service = AIService()
