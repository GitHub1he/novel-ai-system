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