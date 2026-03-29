from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
import json
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exception_handler import BusinessException, NotFoundException
from app.models.user import User
from app.core.logger import logger
from app.models.world_setting import WorldSetting
from app.core.permissions import get_project, require_project, get_world_setting, require_world_setting
from app.schemas.world_setting import WorldSettingCreate, WorldSettingUpdate, WorldSettingResponse, WorldSettingListResponse

router = APIRouter(prefix="/world-settings", tags=["世界观设定"])


@router.post("/create", summary="创建世界观设定")
def create_world_setting(
    setting: WorldSettingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新的世界观设定
    - 管理员可在任何项目中创建世界观设定
    - 普通用户只能在自己的项目中创建世界观设定
    """
    try:
        # 验证项目权限（统一权限检查）
        project = require_project(setting.project_id, current_user, db)

        # 转换 attributes 和 related_entities 为 JSON 字符串
        setting_data = setting.model_dump()
        if setting_data.get('attributes'):
            setting_data['attributes'] = json.dumps(setting_data['attributes'], ensure_ascii=False)
        if setting_data.get('related_entities'):
            setting_data['related_entities'] = json.dumps(setting_data['related_entities'], ensure_ascii=False)

        db_setting = WorldSetting(**setting_data)
        db.add(db_setting)
        db.commit()
        db.refresh(db_setting)

        logger.info(f"创建世界观设定成功: {db_setting.name} (ID: {db_setting.id})")

        return {
            "code": 200,
            "message": "创建成功",
            "data": {
                "id": db_setting.id,
                "project_id": db_setting.project_id,
                "name": db_setting.name,
                "setting_type": db_setting.setting_type.value if hasattr(db_setting.setting_type, 'value') else str(db_setting.setting_type),
                "description": db_setting.description,
                "attributes": db_setting.attributes if db_setting.attributes else None,
                "related_entities": db_setting.related_entities if db_setting.related_entities else None,
                "is_core_rule": db_setting.is_core_rule,
                "image": db_setting.image,
                "created_at": db_setting.created_at.isoformat() if db_setting.created_at else None,
                "updated_at": db_setting.updated_at.isoformat() if db_setting.updated_at else None,
            }
        }
    except ValueError as e:
        raise BusinessException(str(e))
    except Exception as e:
        raise


@router.get("/list/{project_id}", summary="获取项目世界观设定列表")
def get_world_settings(
    project_id: int,
    project = Depends(get_project),
    db: Session = Depends(get_db)
):
    """
    获取项目的所有世界观设定
    - 管理员可访问任何项目的世界观设定
    - 普通用户只能访问自己项目的世界观设定
    """
    try:
        settings = db.query(WorldSetting).filter(
            WorldSetting.project_id == project_id
        ).order_by(WorldSetting.setting_type, WorldSetting.id).all()

        total = db.query(WorldSetting).filter(
            WorldSetting.project_id == project_id
        ).count()

        logger.info(f"获取世界观设定列表成功: project_id={project_id}, count={len(settings)}")

        setting_list = []
        for s in settings:
            setting_dict = {
                "id": s.id,
                "project_id": s.project_id,
                "name": s.name,
                "setting_type": s.setting_type.value if hasattr(s.setting_type, 'value') else str(s.setting_type),
                "description": s.description,
                "attributes": s.attributes if s.attributes else None,
                "related_entities": s.related_entities if s.related_entities else None,
                "is_core_rule": s.is_core_rule,
                "image": s.image,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            }
            setting_list.append(setting_dict)

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "settings": setting_list,
                "total": total
            }
        }
    except Exception as e:
        raise


@router.get("/detail/{setting_id}", summary="获取世界观设定详情")
def get_world_setting_detail(
    setting = Depends(get_world_setting)
):
    """
    获取世界观设定详情
    - 管理员可访问任何世界观设定
    - 普通用户只能访问自己项目的世界观设定
    """
    try:
        logger.info(f"获取世界观设定详情成功: {setting.name} (ID: {setting.id})")

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "id": setting.id,
                "project_id": setting.project_id,
                "name": setting.name,
                "setting_type": setting.setting_type.value if hasattr(setting.setting_type, 'value') else str(setting.setting_type),
                "description": setting.description,
                "attributes": setting.attributes if setting.attributes else None,
                "related_entities": setting.related_entities if setting.related_entities else None,
                "is_core_rule": setting.is_core_rule,
                "image": setting.image,
                "created_at": setting.created_at.isoformat() if setting.created_at else None,
                "updated_at": setting.updated_at.isoformat() if setting.updated_at else None,
            }
        }
    except NotFoundException:
        raise
    except Exception as e:
        raise


@router.post("/update/{setting_id}", summary="更新世界观设定")
def update_world_setting(
    setting_update: WorldSettingUpdate,
    setting = Depends(require_world_setting),
    db: Session = Depends(get_db)
):
    """
    更新世界观设定信息
    - 管理员可修改任何世界观设定
    - 普通用户只能修改自己项目的世界观设定
    """
    try:
        # 更新设定信息
        update_data = setting_update.model_dump(exclude_unset=True)

        # 处理 attributes 和 related_entities
        if 'attributes' in update_data and update_data['attributes'] is not None:
            update_data['attributes'] = json.dumps(update_data['attributes'], ensure_ascii=False)
        if 'related_entities' in update_data and update_data['related_entities'] is not None:
            update_data['related_entities'] = json.dumps(update_data['related_entities'], ensure_ascii=False)

        for field, value in update_data.items():
            setattr(setting, field, value)

        db.commit()
        db.refresh(setting)

        logger.info(f"更新世界观设定成功: {setting.name} (ID: {setting_id})")

        return {
            "code": 200,
            "message": "更新成功",
            "data": {
                "id": setting.id,
                "project_id": setting.project_id,
                "name": setting.name,
                "setting_type": setting.setting_type.value if hasattr(setting.setting_type, 'value') else str(setting.setting_type),
                "description": setting.description,
                "attributes": setting.attributes if setting.attributes else None,
                "related_entities": setting.related_entities if setting.related_entities else None,
                "is_core_rule": setting.is_core_rule,
                "image": setting.image,
                "created_at": setting.created_at.isoformat() if setting.created_at else None,
                "updated_at": setting.updated_at.isoformat() if setting.updated_at else None,
            }
        }
    except NotFoundException:
        raise
    except ValueError as e:
        raise BusinessException(str(e))
    except Exception as e:
        raise


@router.post("/del/{setting_id}", summary="删除世界观设定")
def delete_world_setting(
    setting = Depends(require_world_setting),
    db: Session = Depends(get_db)
):
    """
    删除世界观设定
    - 管理员可删除任何世界观设定
    - 普通用户只能删除自己项目的世界观设定
    """
    try:
        # 如果是核心规则，不允许删除
        if setting.is_core_rule == 1:
            raise BusinessException("核心规则不可删除")

        setting_name = setting.name
        db.delete(setting)
        db.commit()

        logger.info(f"删除世界观设定成功: {setting_name} (ID: {setting.id})")

        return {
            "code": 200,
            "message": "删除成功",
            "data": None
        }
    except NotFoundException:
        raise
    except BusinessException:
        raise
    except Exception as e:
        raise
