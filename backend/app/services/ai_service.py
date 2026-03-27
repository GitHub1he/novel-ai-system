from openai import OpenAI
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.project import Project
from app.models.character import Character
from app.models.world_setting import WorldSetting
from app.models.plot_node import PlotNode
from app.models.chapter import Chapter
from app.core.websocket_manager import send_websocket_message
from typing import List, Dict, Optional
import json
import uuid
import asyncio
import logging
import os

logger = logging.getLogger(__name__)


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
        # 加载提示词配置
        self.prompts_config = self._load_prompts_config()

    def _load_prompts_config(self) -> dict:
        """
        加载提示词配置文件

        Returns:
            提示词配置字典
        """
        try:
            # 获取 app 目录（services 的上级目录）
            current_dir = os.path.dirname(os.path.abspath(__file__))
            app_dir = os.path.dirname(current_dir)
            config_path = os.path.join(app_dir, 'prompts_config.json')

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logger.info(f"成功加载提示词配置文件: {config_path}")
                return config.get('prompts', {})
        except FileNotFoundError:
            logger.warning(f"提示词配置文件未找到: {config_path}，将使用内置提示词")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"提示词配置文件格式错误: {e}")
            return {}
        except Exception as e:
            logger.error(f"加载提示词配置文件失败: {e}")
            return {}

    def _get_prompt(self, prompt_key: str, default: str = "") -> str:
        """
        获取提示词模板

        Args:
            prompt_key: 提示词键名
            default: 默认提示词（配置加载失败时使用）

        Returns:
            提示词模板
        """
        return self.prompts_config.get(prompt_key, default)

    def _format_prompt(self, template: str, **kwargs) -> str:
        """
        格式化提示词模板

        Args:
            template: 提示词模板
            **kwargs: 模板变量

        Returns:
            格式化后的提示词
        """
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.error(f"格式化提示词失败，缺少变量: {e}")
            return template

    def _build_context(self, project_data: dict, characters: list, world_settings: list) -> str:
        """构建AI生成的上下文"""
        context_parts = []

        # 项目基础信息
        if project_data:
            context_parts.append(f"## 📚 小说信息\n")
            context_parts.append(f"书名：{project_data.get('title', '')}\n")
            context_parts.append(f"类型：{project_data.get('genre', '')}\n")
            context_parts.append(f"简介：{project_data.get('summary', '')}\n")
            if project_data.get('style'):
                context_parts.append(f"文风要求：{project_data.get('style')}\n")
            context_parts.append("\n")

        # 人物信息（更详细的展示）
        if characters:
            context_parts.append(f"## 👥 主要人物\n")
            for char in characters[:10]:  # 限制人物数量
                char_info = f"**{char.get('name')}**"
                if char.get('role'):
                    role_map = {
                        'protagonist': '主角',
                        'antagonist': '反派',
                        'supporting': '配角',
                        'minor': '次要角色'
                    }
                    role = role_map.get(char.get('role'), char.get('role'))
                    char_info += f"（{role}）"

                char_info += "\n"

                if char.get('appearance'):
                    char_info += f"- 外貌：{char.get('appearance')}\n"
                if char.get('personality'):
                    char_info += f"- 性格：{char.get('personality')}\n"
                if char.get('identity'):
                    char_info += f"- 身份：{char.get('identity')}\n"
                if char.get('core_motivation'):
                    char_info += f"- 核心动机：{char.get('core_motivation')}\n"

                context_parts.append(char_info)
            context_parts.append("\n")

        # 世界观设定（更详细的展示）
        if world_settings:
            context_parts.append(f"## 🌍 世界观设定\n")
            # 按类型分组
            grouped_settings = {}
            for setting in world_settings[:20]:  # 限制设定数量
                setting_type = setting.get('type', 'other')
                if setting_type not in grouped_settings:
                    grouped_settings[setting_type] = []
                grouped_settings[setting_type].append(setting)

            # 中文类型映射
            type_map = {
                'era': '时代背景',
                'region': '地域设定',
                'rule': '核心规则',
                'culture': '文化习俗',
                'power': '权力结构',
                'location': '重要地点',
                'faction': '势力组织',
                'item': '重要物品',
                'event': '历史事件'
            }

            for setting_type, settings in grouped_settings.items():
                type_name = type_map.get(setting_type, setting_type)
                context_parts.append(f"\n### {type_name}\n")
                for setting in settings:
                    context_parts.append(f"- **{setting.get('name', '未命名')}**")
                    if setting.get('is_core'):
                        context_parts.append(" ⭐[核心规则]")
                    context_parts.append("\n")
                    if setting.get('description'):
                        context_parts.append(f"  {setting.get('description')}\n")

            context_parts.append("\n")

        # 添加创作提示
        context_parts.append("\n## ✍️ 创作要求\n")
        context_parts.append("1. 严格遵循以上人物设定和世界观规则\n")
        context_parts.append("2. 保持人物性格一致，言行符合其设定\n")
        context_parts.append("3. 尊重核心规则，不要自相矛盾\n")
        context_parts.append("4. 细节描写要丰富，对话要符合人物性格\n")
        context_parts.append("5. 根据用户提示词进行创作，但要结合设定\n")

        return "".join(context_parts)

    def generate_chapter(
        self,
        prompt: str,
        context: str,
        word_count: int = 2000,
        style: Optional[str] = None
    ) -> str:
        """生成章节内容（旧版本，向后兼容）"""
        if not self.client:
            raise ValueError("AI服务未配置，请设置OPENAI_API_KEY")

        # 从配置文件获取模板
        template = self._get_prompt('old_chapter_generation', "")
        if not template:
            # 内置默认模板
            template = """你是一个专业的小说创作助手。根据以下设定和用户要求，创作小说内容。

{context}

创作要求：
1. 字数约{word_count}字
2. 保持人物性格一致
3. 遵守世界观设定
{style_section}
"""

        style_section = f"4. 文风：{style}" if style else ""
        system_prompt = self._format_prompt(
            template,
            context=context,
            word_count=word_count,
            style_section=style_section
        )

        try:
            # 计算max_tokens - 中文通常 1 token ≈ 0.7-1 个中文字符
            # 使用 word_count * 3.5 确保达到目标字数
            # 注意：智谱AI推理模型需要额外的推理tokens（约600-1000），所以至少要预留3000以上
            max_tokens = min(max(int(word_count * 3.5), 3000), 16000)

            logger.info(f"===== 文本生成调用参数 =====")
            logger.info(f"模型: {settings.AI_MODEL}")
            logger.info(f"word_count: {word_count}")
            logger.info(f"max_tokens: {max_tokens}")
            logger.info(f"\n===== 系统提示词 =====\n{system_prompt}\n")
            logger.info(f"\n===== 用户提示词 =====\n{prompt}\n")

            response = self.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=max_tokens,
                extra_body={
                    "thinking": {
                        "type": "disabled"  # 关闭思考模式，直接生成内容
                    }
                }
            )

            logger.info(f"===== 文本生成响应 =====")
            logger.info(f"响应对象类型: {type(response)}")
            logger.info(f"响应对象 (str): {str(response)[:1000]}")

            # 尝试转换响应为字典以查看完整结构
            try:
                if hasattr(response, 'model_dump'):
                    response_dict = response.model_dump()
                    logger.info(f"响应有 choices: {len(response_dict.get('choices', []))}")
                    if response_dict.get('choices'):
                        first_choice = response_dict['choices'][0]
                        logger.info(f"第一个choice的keys: {first_choice.keys()}")
                        if 'message' in first_choice:
                            message_obj = first_choice['message']
                            logger.info(f"message对象的keys: {message_obj.keys() if isinstance(message_obj, dict) else 'not a dict'}")
                            logger.info(f"message.content存在: {'content' in message_obj if isinstance(message_obj, dict) else hasattr(message_obj, 'content')}")
                            if isinstance(message_obj, dict) and 'content' in message_obj:
                                logger.info(f"message.content的值: {repr(message_obj['content'][:200]) if message_obj['content'] else 'None'}")
            except Exception as e:
                logger.warning(f"无法转换响应为字典: {e}")

            if hasattr(response, 'usage') and response.usage:
                logger.info(f"prompt_tokens: {response.usage.prompt_tokens}")
                logger.info(f"completion_tokens: {response.usage.completion_tokens}")
                logger.info(f"total_tokens: {response.usage.total_tokens}")

            # 检查choices结构
            logger.info(f"choices数量: {len(response.choices)}")
            logger.info(f"第一个choice类型: {type(response.choices[0])}")
            logger.info(f"第一个choice的message类型: {type(response.choices[0].message)}")

            content = response.choices[0].message.content

            # 如果 content 为空，尝试从 reasoning_content 获取（智谱推理模型）
            if not content and hasattr(response.choices[0].message, 'reasoning_content'):
                reasoning = response.choices[0].message.reasoning_content
                if reasoning:
                    logger.warning(f"content为空，尝试从reasoning_content获取内容（长度：{len(reasoning)}）")
                    # 推理内容可能需要进一步处理，这里先作为后备
                    content = reasoning
                    logger.info(f"注意：使用的是推理内容而非最终答案")

            logger.info(f"生成内容长度: {len(content) if content else 0}")
            logger.info(f"生成内容前200字符: {content[:200] if content else '空内容'}")

            return content
        except Exception as e:
            logger.error(f"文本生成失败: {str(e)}")
            raise Exception(f"AI生成失败: {str(e)}")

    def generate_outline(
        self,
        project_info: dict,
        chapter_count: int = 10
    ) -> List[Dict]:
        """生成大纲"""
        if not self.client:
            raise ValueError("AI服务未配置，请设置OPENAI_API_KEY")

        # 从配置文件获取模板，如果配置为空则使用内置默认值
        template = self._get_prompt('outline_generation', "")
        if not template:
            # 内置默认模板（配置加载失败时的后备方案）
            template = """为一本{genre}小说生成{chapter_count}章的大纲。
书名：《{title}》
简介：{summary}

请生成每章的标题和简要情节描述，以JSON格式返回。"""

        prompt = self._format_prompt(
            template,
            genre=project_info.get('genre', ''),
            title=project_info.get('title', ''),
            summary=project_info.get('summary', ''),
            chapter_count=chapter_count
        )

        try:
            response = self.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"},
                extra_body={
                    "thinking": {
                        "type": "disabled"  # 关闭思考模式
                    }
                }
            )

            result = response.choices[0].message.content
            return json.loads(result).get("chapters", [])
        except Exception as e:
            raise Exception(f"大纲生成失败: {str(e)}")

    def expand_content(self, content: str, target_words: int = 3000) -> str:
        """扩写内容"""
        if not self.client:
            raise ValueError("AI服务未配置，请设置OPENAI_API_KEY")

        # 从配置文件获取模板，如果配置为空则使用内置默认值
        template = self._get_prompt('content_expansion', "")
        if not template:
            # 内置默认模板（配置加载失败时的后备方案）
            template = """请将以下内容扩写到{target_words}字左右，保持原有的情节和人物性格不变：

{content}"""

        prompt = self._format_prompt(template, content=content, target_words=target_words)

        try:
            response = self.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=target_words * 2,
                extra_body={
                    "thinking": {
                        "type": "disabled"  # 关闭思考模式
                    }
                }
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
                # 从配置文件获取系统提示词模板
                system_template = self._get_prompt('context_analysis_system', "")
                if not system_template:
                    # 内置默认模板
                    system_template = """你是一个专业的小说创作助手。请根据项目信息和情节方向，分析并推荐最适合的角色、世界观设定和情节节点。

请严格按照JSON格式返回，包含以下字段：
- suggested_characters: 推荐的角色ID列表（最多10个）
- suggested_world_settings: 推荐的世界观设定ID列表（最多10个）
- suggested_plot_nodes: 推荐的情节节点ID列表（最多10个）

请确保推荐的实体与当前情节方向相符。"""

                response = self.client.chat.completions.create(
                    model=settings.AI_MODEL,
                    messages=[
                        {"role": "system", "content": system_template},
                        {"role": "user", "content": analysis_prompt}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"},
                    extra_body={
                        "thinking": {
                            "type": "disabled"  # 关闭思考模式
                        }
                    }
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

    def _parse_attributes(self, attributes):
        """解析attributes字段，确保返回字典"""
        if attributes is None:
            return {}
        if isinstance(attributes, dict):
            return attributes
        if isinstance(attributes, str):
            try:
                import json
                return json.loads(attributes)
            except:
                return {}
        return {}

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
                    "attributes": self._parse_attributes(setting.attributes),
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

    def generate_chapter_versions(self, request: dict, db: SessionLocal) -> tuple[List[Dict], Dict]:
        """
        生成多个版本的章节内容（同步版本）

        Args:
            request: ChapterGenerateRequest字典格式
            db: 数据库会话

        Returns:
            tuple: (版本列表, 使用的上下文字典)
        """
        from app.schemas.content_generation import FirstChapterMode, ContinueMode

        if not self.client:
            raise ValueError("AI服务未配置，请设置OPENAI_API_KEY")

        # 构建生成上下文
        context_str, context_used = self._build_generation_context(request, db)

        # 生成多个版本
        versions = []
        base_temperature = request.get('temperature', 0.8)
        version_count = min(request.get('versions', 3), 3)  # 最多3个版本

        for i in range(version_count):
            temperature = base_temperature + (i * 0.05)  # 温度递增：0.8, 0.85, 0.9

            # 生成系统提示
            system_prompt = self._build_system_prompt(request, context_str)

            # 生成用户提示
            user_prompt = self._build_user_prompt(request)

            try:
                # 计算max_tokens
                # 中文通常 1 token ≈ 0.7-1 个中文字符
                # 为了确保达到目标字数，使用 word_count * 3.5
                # 注意：智谱AI推理模型需要额外的推理tokens（约600-1000），所以至少要预留2000以上
                word_count = request.get('word_count', 2000)
                max_tokens = min(max(int(word_count * 3.5), 3000), 16000)

                response = self.client.chat.completions.create(
                    model=settings.AI_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    extra_body={
                        "thinking": {
                            "type": "disabled"  # 关闭思考模式，直接生成内容
                        }
                    }
                )

                content = response.choices[0].message.content
                # 不在生成版本时生成摘要，只在保存时生成，避免多次调用AI
                summary = ""  # 留空，保存时再生成

                versions.append({
                    "version_id": str(uuid.uuid4()),
                    "content": content,
                    "word_count": len(content),
                    "summary": summary
                })

            except Exception as e:
                # 如果某个版本生成失败，创建空版本
                versions.append({
                    "version_id": str(uuid.uuid4()),
                    "content": f"生成失败: {str(e)}",
                    "word_count": 0,
                    "summary": "生成失败"
                })

        return versions, context_used

    async def generate_chapter_versions_async(
        self,
        request: dict,
        db: SessionLocal,
        task_id: str
    ) -> tuple[List[Dict], Dict]:
        """
        异步生成多个版本的章节内容，支持进度推送

        Args:
            request: ChapterGenerateRequest字典格式
            db: 数据库会话
            task_id: 任务ID，用于WebSocket推送

        Returns:
            tuple: (版本列表, 使用的上下文字典)
        """
        from app.schemas.content_generation import FirstChapterMode, ContinueMode

        if not self.client:
            raise ValueError("AI服务未配置，请设置OPENAI_API_KEY")

        # 构建生成上下文
        context_str, context_used = self._build_generation_context(request, db)

        # 生成多个版本
        versions = []
        base_temperature = request.get('temperature', 0.8)
        version_count = min(request.get('versions', 3), 3)  # 最多3个版本

        # 发送版本开始事件
        await send_websocket_message(task_id, "version_started", {
            "message": f"开始生成第1个版本",
            "current_version": 1,
            "total_versions": version_count
        })

        for i in range(version_count):
            version_number = i + 1
            temperature = base_temperature + (i * 0.05)  # 温度递增：0.8, 0.85, 0.9

            # 发送版本生成开始事件
            progress = (i / version_count) * 100
            await send_websocket_message(task_id, "version_started", {
                "message": f"开始生成第{version_number}个版本",
                "version_number": version_number,
                "total_versions": version_count,
                "progress": progress,
                "temperature": temperature
            })

            # 生成系统提示
            system_prompt = self._build_system_prompt(request, context_str)

            # 生成用户提示
            user_prompt = self._build_user_prompt(request)

            try:
                # 模拟异步生成（实际API调用是同步的，这里用asyncio.sleep来模拟）
                await asyncio.sleep(0.5)  # 模拟生成耗时

                # 计算max_tokens
                # 中文通常 1 token ≈ 0.7-1 个中文字符
                # 为了确保达到目标字数，使用 word_count * 3.5
                # 注意：智谱AI推理模型需要额外的推理tokens（约600-1000），所以至少要预留2000以上
                word_count = request.get('word_count', 2000)
                max_tokens = min(max(int(word_count * 3.5), 3000), 16000)

                # 打印调试日志
                logger.info(f"===== AI生成调用参数 =====")
                logger.info(f"模型: {settings.AI_MODEL}")
                logger.info(f"temperature: {temperature}")
                logger.info(f"max_tokens: {max_tokens}")
                logger.info(f"\n===== 系统提示词 =====\n{system_prompt}\n")
                logger.info(f"\n===== 用户提示词 =====\n{user_prompt}\n")

                response = self.client.chat.completions.create(
                    model=settings.AI_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    extra_body={
                        "thinking": {
                            "type": "disabled"  # 关闭思考模式，直接生成内容
                        }
                    }
                )

                logger.info(f"===== AI响应 =====")
                logger.info(f"响应对象类型: {type(response)}")
                logger.info(f"choices 数量: {len(response.choices)}")

                # 记录 usage 信息
                if hasattr(response, 'usage'):
                    logger.info(f"usage: {response.usage}")
                    if response.usage:
                        logger.info(f"prompt_tokens: {response.usage.prompt_tokens}")
                        logger.info(f"completion_tokens: {response.usage.completion_tokens}")
                        logger.info(f"total_tokens: {response.usage.total_tokens}")

                # 尝试将响应转换为字典以查看完整结构
                try:
                    if hasattr(response, 'model_dump'):
                        response_dict = response.model_dump()
                        logger.info(f"响应字典结构 (model_dump): {response_dict}")
                    elif hasattr(response, 'dict'):
                        response_dict = response.dict()
                        logger.info(f"响应字典结构 (dict): {response_dict}")
                except Exception as dump_error:
                    logger.warning(f"无法转换为字典: {dump_error}")

                logger.info(f"响应对象 (str): {str(response)}")

                if len(response.choices) > 0:
                    choice = response.choices[0]
                    logger.info(f"choice 对象: {choice}")

                    # 尝试将 choice 转换为字典
                    try:
                        if hasattr(choice, 'model_dump'):
                            choice_dict = choice.model_dump()
                            logger.info(f"choice 完整字典结构: {choice_dict}")
                        elif hasattr(choice, 'dict'):
                            choice_dict = choice.dict()
                            logger.info(f"choice 完整字典结构: {choice_dict}")
                    except Exception as dump_error:
                        logger.warning(f"无法将 choice 转换为字典: {dump_error}")
                    logger.info(f"message 对象: {choice.message}")
                    logger.info(f"message.content 类型: {type(choice.message.content)}")
                    logger.info(f"message.content 长度: {len(choice.message.content) if choice.message.content else 0}")

                    content = choice.message.content

                    # 如果 content 是 None 或空，尝试其他字段
                    if not content:
                        logger.warning("message.content 为空，尝试其他字段...")
                        logger.info(f"choice 的所有属性: {[attr for attr in dir(choice) if not attr.startswith('_')]}")
                        logger.info(f"message 的所有属性: {[attr for attr in dir(choice.message) if not attr.startswith('_')]}")

                        # 检查智谱AI推理模型的特殊字段
                        # 1. reasoning_content - 推理内容
                        if hasattr(choice.message, 'reasoning_content'):
                            content = choice.message.reasoning_content
                            logger.info(f"从 message.reasoning_content 获取内容，长度: {len(content) if content else 0}")

                        # 2. text 字段
                        elif hasattr(choice, 'text'):
                            content = choice.text
                            logger.info(f"从 choice.text 获取内容，长度: {len(content) if content else 0}")

                        # 3. message.text 字段
                        elif hasattr(choice.message, 'text'):
                            content = choice.message.text
                            logger.info(f"从 message.text 获取内容，长度: {len(content) if content else 0}")

                        # 4. 检查原始字典
                        elif 'choice_dict' in locals() and isinstance(choice_dict, dict):
                            logger.info(f"尝试从字典中查找内容字段")
                            logger.info(f"choice_dict keys: {choice_dict.keys()}")
                            if 'message' in choice_dict and isinstance(choice_dict['message'], dict):
                                msg_dict = choice_dict['message']
                                logger.info(f"message_dict keys: {msg_dict.keys()}")
                                for key in ['content', 'text', 'reasoning_content', 'body']:
                                    if key in msg_dict and msg_dict[key]:
                                        content = msg_dict[key]
                                        logger.info(f"从 message.{key} 获取内容，长度: {len(content) if content else 0}")
                                        break

                        # 5. 最后尝试：直接打印原始响应
                        else:
                            logger.error("未找到任何内容字段！")
                            logger.info(f"原始choice对象: {choice}")
                            logger.info(f"原始message对象: {choice.message}")

                    logger.info(f"最终生成内容长度: {len(content) if content else 0}")
                    logger.info(f"最终生成内容前200字符: {content[:200] if content else '空内容'}")
                else:
                    logger.error("响应中没有任何 choices!")
                    content = ""

                # 不在生成版本时生成摘要，只在保存时生成，避免多次调用AI
                summary = ""  # 留空，保存时再生成

                # 发送版本生成完成事件
                version_progress = ((i + 1) / version_count) * 100
                await send_websocket_message(task_id, "version_generated", {
                    "message": f"第{version_number}个版本生成完成",
                    "version_number": version_number,
                    "total_versions": version_count,
                    "progress": version_progress,
                    "version_id": str(uuid.uuid4()),
                    "word_count": len(content)
                })

                versions.append({
                    "version_id": str(uuid.uuid4()),
                    "content": content,
                    "word_count": len(content),
                    "summary": summary
                })

            except Exception as e:
                # 打印详细错误日志
                logger.error(f"===== AI生成失败 =====")
                logger.error(f"版本序号: {version_number}")
                logger.error(f"错误类型: {type(e).__name__}")
                logger.error(f"错误信息: {str(e)}")
                logger.error(f"错误详情: {repr(e)}")

                # 如果某个版本生成失败，创建空版本并发送错误事件
                await send_websocket_message(task_id, "error", {
                    "message": f"第{version_number}个版本生成失败: {str(e)}",
                    "version_number": version_number,
                    "error": str(e)
                })

                versions.append({
                    "version_id": str(uuid.uuid4()),
                    "content": f"生成失败: {str(e)}",
                    "word_count": 0,
                    "summary": "生成失败"
                })

        return versions, context_used

    def _build_generation_context(self, request: dict, db: SessionLocal) -> tuple[str, Dict]:
        """
        构建AI生成的上下文

        Args:
            request: 请求参数
            db: 数据库会话

        Returns:
            tuple: (上下文字符串, 使用的上下文信息)
        """
        from app.schemas.content_generation import FirstChapterMode, ContinueMode

        project_id = request['project_id']
        chapter_number = request['chapter_number']

        # 获取项目信息
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"项目ID {project_id} 不存在")

        # 构建基础项目信息
        project_info = {
            "title": project.title,
            "genre": project.genre,
            "summary": project.summary or "",
            "style": project.style or "通俗"
        }

        context_parts = []
        context_used = {
            "previous_chapter": None,
            "characters": [],
            "world_settings": [],
            "plot_nodes": []
        }

        # 判断是首章还是续写
        if request.get('first_chapter_mode'):
            # 首章模式
            first_chapter_mode = request['first_chapter_mode']
            context_parts.append(f"## 首章生成模式\n")
            context_parts.append(f"开篇场景：{first_chapter_mode.get('opening_scene', '')}\n")
            if first_chapter_mode.get('key_elements'):
                context_parts.append(f"核心要素：{', '.join(first_chapter_mode['key_elements'])}\n")
            if first_chapter_mode.get('tone'):
                context_parts.append(f"开篇基调：{first_chapter_mode['tone']}\n")

        elif request.get('continue_mode'):
            # 续写模式
            continue_mode = request['continue_mode']
            previous_chapter_id = continue_mode['previous_chapter_id']
            previous_chapter = db.query(Chapter).filter(Chapter.id == previous_chapter_id).first()

            if previous_chapter and previous_chapter.content:
                # 只取最后800个字符
                previous_context = previous_chapter.content[-800:].strip()
                context_parts.append(f"## 前文内容\n")
                context_parts.append(f"{previous_context}\n")
                context_used["previous_chapter"] = {
                    "chapter_number": previous_chapter.chapter_number,
                    "last_content": previous_context
                }

            context_parts.append(f"\n## 续写模式\n")
            context_parts.append(f"衔接方式：{continue_mode.get('transition', 'immediate')}\n")
            context_parts.append(f"情节方向：{continue_mode.get('plot_direction', '')}\n")
            if continue_mode.get('conflict_point'):
                context_parts.append(f"核心冲突：{continue_mode['conflict_point']}\n")

        # 添加项目基础信息
        context_parts.append(f"\n## 小说信息\n")
        context_parts.append(f"书名：{project_info['title']}\n")
        context_parts.append(f"类型：{project_info['genre']}\n")
        context_parts.append(f"简介：{project_info['summary']}\n")
        context_parts.append(f"文风：{project_info['style']}\n")

        # 添加人物信息
        characters = []
        if request.get('featured_characters'):
            # 使用指定的人物
            character_ids = request['featured_characters']
            characters = db.query(Character).filter(
                Character.id.in_(character_ids),
                Character.project_id == project_id
            ).all()
        else:
            # 使用相关人物（简化处理，使用前5个）
            characters = db.query(Character).filter(
                Character.project_id == project_id
            ).limit(5).all()

        if characters:
            context_parts.append(f"\n## 人物设定\n")
            # 按角色类型排序，主角排在前面
            role_priority = {
                'protagonist': 0,  # 主角
                'supporting': 1,   # 配角
                'antagonist': 2,   # 反派
                'minor': 3         # 次要角色
            }
            characters.sort(key=lambda c: role_priority.get(c.role.value if hasattr(c.role, 'value') else c.role, 99))

            for char in characters:
                # 角色类型中文映射
                role_map = {
                    'protagonist': '【主角】',
                    'antagonist': '【反派】',
                    'supporting': '【配角】',
                    'minor': '【次要角色】'
                }
                role_label = role_map.get(char.role.value if hasattr(char.role, 'value') else char.role, '')

                # 构建详细的人物信息
                char_info = f"- {char.name} {role_label}\n"

                # 基本信息
                if char.age or char.gender:
                    basic_info = []
                    if char.gender:
                        basic_info.append(char.gender)
                    if char.age:
                        basic_info.append(f"{char.age}岁")
                    if basic_info:
                        char_info += f"  基本信息：{', '.join(basic_info)}\n"

                # 外貌
                if char.appearance:
                    char_info += f"  外貌：{char.appearance}\n"

                # 身份
                if char.identity:
                    char_info += f"  身份：{char.identity}\n"

                # 性格
                if char.personality:
                    char_info += f"  性格：{char.personality}\n"

                # 核心动机
                if char.core_motivation:
                    char_info += f"  核心动机：{char.core_motivation}\n"

                context_parts.append(char_info)
                context_used["characters"].append(char.name)

        # 添加世界观设定
        world_settings = []
        if request.get('related_world_settings'):
            # 使用指定的世界观
            setting_ids = request['related_world_settings']
            world_settings = db.query(WorldSetting).filter(
                WorldSetting.id.in_(setting_ids),
                WorldSetting.project_id == project_id
            ).all()
        else:
            # 使用相关世界观（简化处理，使用前3个）
            world_settings = db.query(WorldSetting).filter(
                WorldSetting.project_id == project_id
            ).limit(3).all()

        if world_settings:
            context_parts.append(f"\n## 世界观设定\n")
            for setting in world_settings:
                context_parts.append(f"- {setting.name}：{setting.description or '暂无描述'}\n")
                context_used["world_settings"].append(setting.name)

        # 添加情节节点
        plot_nodes = []
        if request.get('related_plot_nodes'):
            # 使用指定的情节节点
            plot_ids = request['related_plot_nodes']
            plot_nodes = db.query(PlotNode).filter(
                PlotNode.id.in_(plot_ids),
                PlotNode.project_id == project_id
            ).all()
        else:
            # 使用相关情节节点（简化处理，使用前5个）
            plot_nodes = db.query(PlotNode).filter(
                PlotNode.project_id == project_id
            ).limit(5).all()

        if plot_nodes:
            context_parts.append(f"\n## 情节节点\n")
            for node in plot_nodes:
                context_parts.append(f"- {node.title}：{node.description or '暂无描述'}\n")
                context_used["plot_nodes"].append(node.title)

        # 添加POV人物信息
        if request.get('pov_character_id'):
            pov_character = db.query(Character).filter(
                Character.id == request['pov_character_id'],
                Character.project_id == project_id
            ).first()
            if pov_character:
                context_parts.append(f"\n## 叙事视角\n")
                context_parts.append(f"POV人物：{pov_character.name}\n")

        # 添加其他要求
        # 优先使用请求中的word_count，否则使用项目的默认设置
        word_count = request.get('word_count') or project.target_words_per_chapter or 2000
        context_parts.append(f"\n## 生成要求\n")
        context_parts.append(f"1. 目标字数：约{word_count}字\n")
        context_parts.append(f"2. 章节序号：第{chapter_number}章\n")

        if request.get('style_intensity'):
            intensity = request['style_intensity']
            context_parts.append(f"3. 风格强度：{intensity}%\n")

        context_parts.append(f"\n请根据以上设定和要求，创作小说内容。")

        return "".join(context_parts), context_used

    def _build_system_prompt(self, request: dict, context: str) -> str:
        """
        构建系统提示词 - 使用配置文件中的模板

        Args:
            request: 请求参数（包含项目信息）
            context: 上下文字符串（包含人物、世界观等，已格式化）

        Returns:
            系统提示词
        """
        # 获取风格强度，用于调整文风强调程度
        style_intensity = request.get('style_intensity', 70)

        # 从配置文件获取模板，如果配置为空则使用内置默认值
        template = self._get_prompt('system_chapter_generation', "")
        if not template:
            # 内置默认模板（配置加载失败时的后备方案）
            template = """你是一个专业的小说创作助手。请严格按照以下设定创作高质量的小说内容。

{context}

【创作规则（必须遵守）】
1. 所有出场人物必须来自上述人物设定，不得擅自添加或修改姓名。
2. 人物性格、语言风格、关系必须与设定一致。
3. 情节推进要自然，避免突兀转折。
4. 综合运用对话、动作、心理描写和环境描写。
5. 每章结尾可适当留白或制造悬念，但要保持整体故事的连贯性。
6. **文风要求（重要）**：必须严格遵循上述"文风"设定，这决定了整部作品的语言风格和叙述基调。风格匹配度要求：{style_intensity}%。

请严格遵守以上设定，创作出引人入胜、符合要求的章节内容。"""

        return self._format_prompt(template, context=context, style_intensity=style_intensity)

    def _build_user_prompt(self, request: dict) -> str:
        """
        构建用户提示词 - 使用配置文件中的模板

        Args:
            request: 请求参数

        Returns:
            用户提示词
        """
        chapter_number = request['chapter_number']
        word_count = request.get('word_count', 2000)
        generation_mode = request.get('mode', 'standard')
        prompt_text = request.get('prompt', '')
        plot_direction = request.get('plot_direction', '')
        previous_summary = request.get('previous_chapter_summary', '')

        # 获取主角信息（从上下文中解析）
        protagonist_info = ""
        if request.get('featured_characters'):
            protagonist_info = "主角姓名请查看人物设定"

        # 根据模式选择合适的模板
        template_key = None
        template_vars = {
            'chapter_number': chapter_number,
            'word_count': word_count
        }

        if generation_mode == 'first_chapter':
            # 首章模式
            if prompt_text:
                template_key = 'user_first_chapter_with_custom'
                template_vars['prompt'] = prompt_text
            else:
                template_key = 'user_first_chapter'

        elif generation_mode == 'continue':
            # 续写模式
            template_vars['plot_direction'] = plot_direction if plot_direction else '根据前文自然发展'
            template_vars['protagonist_info'] = protagonist_info
            template_vars['previous_summary'] = (
                previous_summary[:300] + "..." if len(previous_summary) > 300
                else previous_summary
            ) if previous_summary else "无"

            if prompt_text:
                template_key = 'user_continue_with_custom'
                template_vars['prompt'] = prompt_text
            elif previous_summary:
                template_key = 'user_continue_with_summary'
            else:
                template_key = 'user_continue'

        else:
            # 标准模式
            if prompt_text:
                template_key = 'user_standard_with_custom'
                template_vars['prompt'] = prompt_text
            else:
                template_key = 'user_standard'

        # 从配置文件获取模板，如果配置为空则使用内置默认值
        template = self._get_prompt(template_key, "")
        if not template:
            # 内置默认模板（配置加载失败时的后备方案）
            template = self._get_default_user_prompt(generation_mode, bool(prompt_text), bool(previous_summary))

        prompt = self._format_prompt(template, **template_vars)

        logger.info(f"===== 构建的用户提示词 =====")
        logger.info(f"章节号: {chapter_number}")
        logger.info(f"生成模式: {generation_mode}")
        logger.info(f"目标字数: {word_count}")
        logger.info(f"情节方向: {plot_direction}")
        logger.info(f"用户提示: {prompt_text}")
        logger.info(f"有前文总结: {bool(previous_summary)}")
        logger.info(f"完整提示词:\n{prompt}\n")

        return prompt

    def _get_default_user_prompt(self, mode: str, has_custom: bool, has_summary: bool) -> str:
        """
        获取内置默认用户提示词（配置加载失败时的后备方案）

        Args:
            mode: 生成模式（first_chapter/continue/standard）
            has_custom: 是否有用户自定义要求
            has_summary: 是否有前文总结

        Returns:
            默认提示词模板
        """
        if mode == 'first_chapter':
            if has_custom:
                return """# 首次生成任务

## 章节信息
- 章节序号：第{chapter_number}章
- 目标字数：约{word_count}字

## 首章要点
1. 引入主角，展示其基本特征（外貌、性格、身份、背景）
2. 建立故事背景和世界观（时代、地点、社会氛围）
3. 设置初始情境或引发事件，推动故事发展
4. 营造故事基调，吸引读者继续阅读

## 创作建议
- 避免大段背景说明，通过情节和细节自然展现设定
- 开头要吸引人，可设置悬念、冲突或引人入胜的场景
- 确保主角在第1章就有足够的戏份和表现
- 结尾可适当留白或制造轻微悬念

## 输出要求
请直接输出第{chapter_number}章正文，不需要额外说明。章节开头标注"第{chapter_number}章"，正文约{word_count}字。

## 用户特别要求
{prompt}"""
            else:
                return """# 首次生成任务

## 章节信息
- 章节序号：第{chapter_number}章
- 目标字数：约{word_count}字

## 首章要点
1. 引入主角，展示其基本特征（外貌、性格、身份、背景）
2. 建立故事背景和世界观（时代、地点、社会氛围）
3. 设置初始情境或引发事件，推动故事发展
4. 营造故事基调，吸引读者继续阅读

## 创作建议
- 避免大段背景说明，通过情节和细节自然展现设定
- 开头要吸引人，可设置悬念、冲突或引人入胜的场景
- 确保主角在第1章就有足够的戏份和表现
- 结尾可适当留白或制造轻微悬念

## 输出要求
请直接输出第{chapter_number}章正文，不需要额外说明。章节开头标注"第{chapter_number}章"，正文约{word_count}字。"""

        elif mode == 'continue':
            base_template = """# 续写任务

## 本次任务
- 章节序号：第{chapter_number}章
- 目标字数：约{word_count}字
- 衔接方式：紧接上一章结尾
{summary_line}- 情节方向：{plot_direction}
- 情感基调：根据故事情节自然呈现

## 续写要点
1. 承接上一章结尾的场景和情节，确保时间和空间连续性
2. 根据前文情节发展方向，推进故事
3. 维持人物性格和行为逻辑的一致性
4. 创造新的情节冲突或转折，保持故事张力
5. 适当运用对话、心理活动、动作描写和环境渲染

## 重要提醒
- 主角姓名：{protagonist_info}
- 其他人物：请查看人物设定，确保姓名和性格一致
- 禁止添加人物设定之外的新角色
- 注意前文已埋下的伏笔和悬念

## 输出要求
请直接输出第{chapter_number}章正文，不需要额外说明。章节开头标注"第{chapter_number}章"，正文约{word_count}字。"""

            if has_custom:
                return base_template + "\n\n## 用户特别要求\n{prompt}"
            elif has_summary:
                summary_line = "- 前文总结：{previous_summary}\n"
                return base_template.format(summary_line=summary_line)
            else:
                summary_line = ""
                return base_template.format(summary_line=summary_line)

        else:  # standard
            if has_custom:
                return """# 创作第{chapter_number}章

## 章节信息
- 章节序号：第{chapter_number}章
- 目标字数：约{word_count}字

## 创作要点
1. 情节完整，有起承转合
2. 人物性格鲜明，行为符合逻辑
3. 场景描写生动，有画面感
4. 对话自然，推动情节发展

## 输出要求
请直接输出第{chapter_number}章正文，章节开头标注"第{chapter_number}章"，正文约{word_count}字。

## 用户特别要求
{prompt}"""
            else:
                return """# 创作第{chapter_number}章

## 章节信息
- 章节序号：第{chapter_number}章
- 目标字数：约{word_count}字

## 创作要点
1. 情节完整，有起承转合
2. 人物性格鲜明，行为符合逻辑
3. 场景描写生动，有画面感
4. 对话自然，推动情节发展

## 输出要求
请直接输出第{chapter_number}章正文，章节开头标注"第{chapter_number}章"，正文约{word_count}字。"""

    def generate_chapter_summary(self, content: str, title: str = "") -> str:
        """
        使用AI生成章节摘要

        Args:
            content: 章节内容
            title: 章节标题（可选）

        Returns:
            内容摘要
        """
        if not content or len(content) < 100:
            return "内容过短，无法生成摘要"

        if not self.client:
            # 如果AI服务未配置，使用简单截取
            summary = content[:200].replace('\n', ' ').strip()
            if len(summary) > 200:
                summary = summary[:197] + "..."
            return summary

        try:
            # 从配置文件获取模板，如果配置为空则使用内置默认值
            template = self._get_prompt('summary_generation', "")
            if not template:
                # 内置默认模板（配置加载失败时的后备方案）
                template = """请为以下小说章节生成一段适合续写的剧情总结（200-300字）：

章节标题：{title}
章节内容：
{content}

要求：
1. **结尾状态**：本章结束时，主要人物在哪里、在做什么、情绪状态如何
2. **关键转折**：本章发生的重要事件和转折点，特别是对后续剧情有影响的内容
3. **未解事项**：本章提出但未解决的问题、悬念、伏笔
4. **人物关系**：人物关系的变化，特别是冲突、alliances、情感变化
5. **续写提示**：基于本章结尾，下一章可能的情节方向

请用叙述性语言写出，重点放在"结尾状态"和"续写提示"上，让下一章的作者能够自然衔接。"""

            # 限制内容长度为2000字符
            content_preview = content[:2000] if len(content) > 2000 else content
            prompt = self._format_prompt(template, title=title, content=content_preview)

            response = self.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500,
                extra_body={
                    "thinking": {
                        "type": "disabled"  # 关闭思考模式
                    }
                }
            )

            summary = response.choices[0].message.content.strip()
            return summary
        except Exception as e:
            # AI生成失败时，使用简单截取
            logger.warning(f"AI生成摘要失败: {str(e)}，使用简单截取")
            summary = content[:200].replace('\n', ' ').strip()
            if len(summary) > 200:
                summary = summary[:197] + "..."
            return summary

    def generate_display_summary(self, content: str, title: str = "") -> str:
        """
        使用AI生成章节展示摘要（用于页面显示）

        Args:
            content: 章节内容
            title: 章节标题（可选）

        Returns:
            展示摘要（100-150字）
        """
        if not content or len(content) < 100:
            return "内容过短，无法生成摘要"

        if not self.client:
            # 如果AI服务未配置，使用简单截取
            summary = content[:150].replace('\n', ' ').strip()
            if len(summary) > 150:
                summary = summary[:147] + "..."
            return summary

        try:
            # 从配置文件获取模板，如果配置为空则使用内置默认值
            template = self._get_prompt('display_summary_generation', "")
            if not template:
                # 内置默认模板（配置加载失败时的后备方案）
                template = """请为以下小说章节生成一段简短的剧情简介（100-150字），用于在页面中展示给读者：

章节标题：{title}
章节内容：
{content}

要求：
1. **简洁明了**：用一两句话概括本章主要情节
2. **读者友好**：面向读者，不包含剧透和写作技术细节
3. **引人入胜**：突出本章的精彩看点，吸引阅读兴趣
4. **中立叙述**：使用第三人称客观叙述
5. **字数控制**：严格控制在100-150字

请直接输出简介内容，不要包含"本章讲述了"等开头词。"""

            # 限制内容长度为2000字符
            content_preview = content[:2000] if len(content) > 2000 else content
            prompt = self._format_prompt(template, title=title, content=content_preview)

            response = self.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=300,  # 300 tokens 足够生成 150 字
                extra_body={
                    "thinking": {
                        "type": "disabled"  # 关闭思考模式
                    }
                }
            )

            display_summary = response.choices[0].message.content.strip()
            return display_summary
        except Exception as e:
            # AI生成失败时，使用简单截取
            logger.warning(f"AI生成展示摘要失败: {str(e)}，使用简单截取")
            summary = content[:150].replace('\n', ' ').strip()
            if len(summary) > 150:
                summary = summary[:147] + "..."
            return summary


# 全局AI服务实例
ai_service = AIService()
