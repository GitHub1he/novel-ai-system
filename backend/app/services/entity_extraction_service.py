from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.character import Character
from app.models.world_setting import WorldSetting
from app.schemas.entity_extraction import (
    ExtractedCharacter,
    ExtractedWorldSetting
)
from app.services.ai_service import AIService
from app.core.config import settings
from app.core.logger import logger
from difflib import SequenceMatcher


class EntityExtractionService:
    """实体提取服务"""

    def __init__(self, ai_service: Optional[AIService] = None):
        self.ai_service = ai_service

    def _is_similar_name(
        self,
        name1: str,
        name2: str,
        threshold: Optional[float] = None
    ) -> bool:
        """
        判断两个名称是否相似

        Args:
            name1: 第一个名称
            name2: 第二个名称
            threshold: 相似度阈值（0-1），默认使用配置文件中的值

        Returns:
            True if similar enough to be considered duplicate
        """
        if threshold is None:
            threshold = settings.ENTITY_SIMILARITY_THRESHOLD

        similarity = SequenceMatcher(None, name1, name2).ratio()
        return similarity >= threshold

    def _deduplicate_characters(
        self,
        detected: List[Dict[str, Any]],
        existing: List[Character]
    ) -> List[Dict[str, Any]]:
        """
        通过名称相似度过滤重复人物

        Args:
            detected: AI 检测到的人物列表
            existing: 数据库中已有人物列表

        Returns:
            过滤后的人物列表
        """
        unique_characters = []

        for detected_char in detected:
            detected_name = detected_char.get("name", "")
            if not detected_name:
                continue

            is_duplicate = False
            for existing_char in existing:
                if self._is_similar_name(detected_name, existing_char.name):
                    is_duplicate = True
                    logger.info(
                        f"跳过重复人物: {detected_name} "
                        f"(相似于 {existing_char.name})"
                    )
                    break

            if not is_duplicate:
                unique_characters.append(detected_char)

        return unique_characters

    def _deduplicate_world_settings(
        self,
        detected: List[Dict[str, Any]],
        existing: List[WorldSetting]
    ) -> List[Dict[str, Any]]:
        """
        通过名称相似度过滤重复世界观设定

        Args:
            detected: AI 检测到的世界观设定列表
            existing: 数据库中已有世界观设定列表

        Returns:
            过滤后的世界观设定列表
        """
        unique_settings = []

        for detected_setting in detected:
            detected_name = detected_setting.get("name", "")
            if not detected_name:
                continue

            is_duplicate = False
            for existing_setting in existing:
                if self._is_similar_name(detected_name, existing_setting.name):
                    is_duplicate = True
                    logger.info(
                        f"跳过重复设定: {detected_name} "
                        f"(相似于 {existing_setting.name})"
                    )
                    break

            if not is_duplicate:
                unique_settings.append(detected_setting)

        return unique_settings

    def _detect_characters(
        self,
        content: str,
        existing_characters: List[Character]
    ) -> List[Dict[str, Any]]:
        """
        使用 AI 检测章节中的人物

        Args:
            content: 章节内容
            existing_characters: 已有人物列表（用于提示 AI）

        Returns:
            检测到的人物列表
        """
        logger.info(f"开始检测人物，AI 服务状态: {self.ai_service is not None}")
        if self.ai_service:
            logger.info(f"AI 客户端状态: {self.ai_service.client is not None}")

        if not self.ai_service or not self.ai_service.client:
            logger.error("AI 服务未初始化，无法检测人物")
            return []

        # 构建已有人物名称列表
        existing_names = [char.name for char in existing_characters]
        existing_str = ", ".join(existing_names) if existing_names else "无"

        # 构建 prompt
        prompt = f"""请分析以下小说章节内容，提取出所有出现的人物。

对于每个人物，请提取以下信息：
- name: 姓名（必须）
- age: 年龄（数字）
- gender: 性别
- appearance: 外貌描述
- identity: 身份/职业
- hometown: 籍贯
- role: 角色类型（protagonist/antagonist/supporting/minor）
  注意：根据人物在故事中的作用判断类型，如果无法确定，默认使用 "supporting"
- personality: 性格特点（逗号分隔的标签）
- core_motivation: 核心动机
- fears: 恐惧的事物
- desires: 渴望的事物

章节内容：
{content}

参考已有的人物名称以避免重复（但请返回所有检测到的人物，系统会在服务端进行最终去重）：
{existing_str}

请以 JSON 格式返回，格式如下：
{{
  "characters": [
    {{
      "name": "张三",
      "age": 25,
      "gender": "男",
      "appearance": "身材高大，眉目清秀",
      "identity": "剑客",
      "role": "supporting"
    }}
  ]
}}

只返回 JSON，不要有其他内容。"""

        try:
            response = self.ai_service.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个专业的小说人物分析助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            result_text = response.choices[0].message.content.strip()

            # 尝试解析 JSON
            import json
            # 移除可能的 markdown 代码块标记
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()

            result = json.loads(result_text)
            characters = result.get("characters", [])

            logger.info(f"AI 检测到 {len(characters)} 个人物")
            return characters

        except json.JSONDecodeError as e:
            logger.error(f"AI 返回的 JSON 解析失败: {e}, 原始内容: {result_text}")
            return []
        except Exception as e:
            logger.error(f"AI 检测人物失败: {e}")
            return []

    def _detect_world_settings(
        self,
        content: str,
        existing_settings: List[WorldSetting]
    ) -> List[Dict[str, Any]]:
        """
        使用 AI 检测章节中的世界观设定

        Args:
            content: 章节内容
            existing_settings: 已有世界观设定列表（用于提示 AI）

        Returns:
            检测到的世界观设定列表
        """
        if not self.ai_service or not self.ai_service.client:
            logger.error("AI 服务未初始化")
            return []

        # 构建已有设定名称列表
        existing_names = [setting.name for setting in existing_settings]
        existing_str = ", ".join(existing_names) if existing_names else "无"

        # 构建 prompt
        prompt = f"""请分析以下小说章节内容，提取出所有提到的世界观设定。

类型包括：
- era: 时代背景
- region: 地域/地点
- rule: 规则（魔法/科技体系）
- culture: 文化习俗
- power: 权力结构
- location: 具体地点
- faction: 势力/组织
- item: 重要物品
- event: 历史事件

对于每个设定，请提取：
- name: 名称（必须）
- setting_type: 类型（从上述类型中选择）
- description: 详细描述
- attributes: 扩展属性（JSON 对象）
- is_core_rule: 是否为核心规则（0或1）

章节内容：
{content}

参考已有的设定名称以避免重复（但请返回所有检测到的设定，系统会在服务端进行最终去重）：
{existing_str}

请以 JSON 格式返回，格式如下：
{{
  "world_settings": [
    {{
      "name": "青云剑派",
      "setting_type": "faction",
      "description": "江湖上著名的剑术门派",
      "attributes": {{"founding_year": "明朝", "location": "华山"}},
      "is_core_rule": 0
    }}
  ]
}}

只返回 JSON，不要有其他内容。"""

        try:
            response = self.ai_service.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个专业的小说世界观分析助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            result_text = response.choices[0].message.content.strip()

            # 尝试解析 JSON
            import json
            # 移除可能的 markdown 代码块标记
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()

            result = json.loads(result_text)
            detected_settings_list = result.get("world_settings", [])

            logger.info(f"AI 检测到 {len(detected_settings_list)} 个世界观设定")
            return detected_settings_list

        except json.JSONDecodeError as e:
            logger.error(f"AI 返回的 JSON 解析失败: {e}, 原始内容: {result_text}")
            return []
        except Exception as e:
            logger.error(f"AI 检测世界观设定失败: {e}")
            return []

    def extract_characters(
        self,
        db: Session,
        project_id: int,
        content: str
    ) -> Dict[str, int]:
        """
        从章节内容中提取并创建人物

        Args:
            db: 数据库会话
            project_id: 项目 ID
            content: 章节内容

        Returns:
            {"added": 数量, "skipped": 数量}
        """
        if not content or not content.strip():
            logger.warning("章节内容为空，跳过人物提取")
            return {"added": 0, "skipped": 0}

        if not db:
            logger.error("数据库会话为空")
            return {"added": 0, "skipped": 0}

        # 获取已有人物
        existing_characters = db.query(Character).filter(
            Character.project_id == project_id
        ).all()

        # AI 检测人物
        detected_characters = self._detect_characters(content, existing_characters)

        if not detected_characters:
            logger.info("AI 未检测到任何人物")
            return {"added": 0, "skipped": 0}

        # 去重
        unique_characters = self._deduplicate_characters(
            detected_characters,
            existing_characters
        )

        # 创建人物
        added_count = 0
        skipped_count = len(detected_characters) - len(unique_characters)

        for char_data in unique_characters:
            try:
                # 验证数据
                validated_char = ExtractedCharacter(**char_data)

                # 创建人物记录
                new_char = Character(
                    project_id=project_id,
                    **validated_char.model_dump(exclude_unset=True)
                )
                db.add(new_char)
                added_count += 1
                logger.info(f"创建人物: {validated_char.name}")

            except Exception as e:
                logger.error(f"创建人物失败: {e}, 数据: {char_data}")
                continue

        try:
            db.commit()
        except Exception as e:
            logger.error(f"提交数据库失败: {e}")
            db.rollback()
            return {"added": 0, "skipped": skipped_count}

        logger.info(f"人物提取完成: 添加 {added_count} 个，跳过 {skipped_count} 个")
        return {"added": added_count, "skipped": skipped_count}

    def extract_world_settings(
        self,
        db: Session,
        project_id: int,
        content: str
    ) -> Dict[str, int]:
        """
        从章节内容中提取并创建世界观设定

        Args:
            db: 数据库会话
            project_id: 项目 ID
            content: 章节内容

        Returns:
            {"added": 数量, "skipped": 数量}
        """
        if not content or not content.strip():
            logger.warning("章节内容为空，跳过世界观设定提取")
            return {"added": 0, "skipped": 0}

        if not db:
            logger.error("数据库会话为空")
            return {"added": 0, "skipped": 0}

        # 获取已有设定
        existing_settings = db.query(WorldSetting).filter(
            WorldSetting.project_id == project_id
        ).all()

        # AI 检测设定
        detected_settings = self._detect_world_settings(content, existing_settings)

        if not detected_settings:
            logger.info("AI 未检测到任何世界观设定")
            return {"added": 0, "skipped": 0}

        # 去重
        unique_settings = self._deduplicate_world_settings(
            detected_settings,
            existing_settings
        )

        # 创建设定
        added_count = 0
        skipped_count = len(detected_settings) - len(unique_settings)

        for setting_data in unique_settings:
            try:
                # 验证数据
                validated_setting = ExtractedWorldSetting(**setting_data)

                # 创建设定记录
                new_setting = WorldSetting(
                    project_id=project_id,
                    **validated_setting.model_dump(exclude_unset=True)
                )
                db.add(new_setting)
                added_count += 1
                logger.info(f"创建世界观设定: {validated_setting.name}")

            except Exception as e:
                logger.error(f"创建世界观设定失败: {e}, 数据: {setting_data}")
                continue

        try:
            db.commit()
        except Exception as e:
            logger.error(f"提交数据库失败: {e}")
            db.rollback()
            return {"added": 0, "skipped": skipped_count}

        logger.info(f"世界观设定提取完成: 添加 {added_count} 个，跳过 {skipped_count} 个")
        return {"added": added_count, "skipped": skipped_count}


# 创建全局服务实例
entity_extraction_service = EntityExtractionService(ai_service=None)