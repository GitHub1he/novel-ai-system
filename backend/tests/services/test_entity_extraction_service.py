import pytest
from app.services.entity_extraction_service import EntityExtractionService
from app.models.character import Character
from app.models.world_setting import WorldSetting

def test_is_similar_name_exact_match():
    """测试完全相同的名称"""
    service = EntityExtractionService()
    assert service._is_similar_name("张三", "张三") == True

def test_is_similar_name_high_similarity():
    """测试高相似度名称"""
    service = EntityExtractionService()
    # "张三" vs "张小三" 相似度约 0.8 >= 0.7，应该相似
    assert service._is_similar_name("张三", "张小三") == True
    # "剑派" vs "剑派" 相似度 1.0 >= 0.7，应该相似
    assert service._is_similar_name("剑派", "剑派") == True

def test_is_similar_name_custom_threshold():
    """测试自定义阈值"""
    service = EntityExtractionService()
    # 使用更低的阈值 0.6
    assert service._is_similar_name("张三", "张小三", threshold=0.6) == True

def test_is_similar_name_empty_strings():
    """测试空字符串"""
    service = EntityExtractionService()
    assert service._is_similar_name("", "") == True