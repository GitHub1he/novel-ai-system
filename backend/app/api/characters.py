from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.exception_handler import BusinessException, NotFoundException
from app.core.logger import logger
from app.models.character import Character
from app.schemas.character import CharacterCreate, CharacterUpdate, CharacterResponse, CharacterListResponse

router = APIRouter(prefix="/characters", tags=["人物管理"])


@router.post("/create", summary="创建人物")
def create_character(character: CharacterCreate, user_id: int = 1, db: Session = Depends(get_db)):
    """创建新人物"""
    try:
        db_character = Character(**character.model_dump())
        db.add(db_character)
        db.commit()
        db.refresh(db_character)

        logger.info(f"创建人物成功: {db_character.name} (ID: {db_character.id})")

        return {
            "code": 200,
            "message": "创建成功",
            "data": {
                "id": db_character.id,
                "project_id": db_character.project_id,
                "name": db_character.name,
                "age": db_character.age,
                "gender": db_character.gender,
                "appearance": db_character.appearance,
                "identity": db_character.identity,
                "hometown": db_character.hometown,
                "role": db_character.role.value if hasattr(db_character.role, 'value') else str(db_character.role),
                "personality": db_character.personality,
                "core_motivation": db_character.core_motivation,
                "fears": db_character.fears,
                "desires": db_character.desires,
                "initial_state": db_character.initial_state,
                "turning_point": db_character.turning_point,
                "final_state": db_character.final_state,
                "speech_style": db_character.speech_style,
                "sample_dialogue": db_character.sample_dialogue,
                "avatar": db_character.avatar,
                "appearance_count": db_character.appearance_count,
                "created_at": db_character.created_at.isoformat() if db_character.created_at else None,
                "updated_at": db_character.updated_at.isoformat() if db_character.updated_at else None,
            }
        }
    except ValueError as e:
        raise BusinessException(str(e))
    except Exception as e:
        raise


@router.get("/list/{project_id}", summary="获取项目人物列表")
def get_characters(project_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    """获取项目的所有人物"""
    try:
        characters = db.query(Character).filter(
            Character.project_id == project_id
        ).order_by(Character.id).all()

        total = db.query(Character).filter(
            Character.project_id == project_id
        ).count()

        logger.info(f"获取人物列表成功: project_id={project_id}, count={len(characters)}")

        character_list = []
        for c in characters:
            character_dict = {
                "id": c.id,
                "project_id": c.project_id,
                "name": c.name,
                "age": c.age,
                "gender": c.gender,
                "appearance": c.appearance,
                "identity": c.identity,
                "hometown": c.hometown,
                "role": c.role.value if hasattr(c.role, 'value') else str(c.role),
                "personality": c.personality,
                "core_motivation": c.core_motivation,
                "fears": c.fears,
                "desires": c.desires,
                "initial_state": c.initial_state,
                "turning_point": c.turning_point,
                "final_state": c.final_state,
                "speech_style": c.speech_style,
                "sample_dialogue": c.sample_dialogue,
                "avatar": c.avatar,
                "appearance_count": c.appearance_count,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
            }
            character_list.append(character_dict)

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "characters": character_list,
                "total": total
            }
        }
    except Exception as e:
        raise


@router.get("/detail/{character_id}", summary="获取人物详情")
def get_character(character_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    """获取人物详情"""
    try:
        character = db.query(Character).filter(
            Character.id == character_id
        ).first()

        if not character:
            raise NotFoundException(f"人物 {character_id} 不存在")

        logger.info(f"获取人物详情成功: {character.name} (ID: {character_id})")

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "id": character.id,
                "project_id": character.project_id,
                "name": character.name,
                "age": character.age,
                "gender": character.gender,
                "appearance": character.appearance,
                "identity": character.identity,
                "hometown": character.hometown,
                "role": character.role.value if hasattr(character.role, 'value') else str(character.role),
                "personality": character.personality,
                "core_motivation": character.core_motivation,
                "fears": character.fears,
                "desires": character.desires,
                "initial_state": character.initial_state,
                "turning_point": character.turning_point,
                "final_state": character.final_state,
                "speech_style": character.speech_style,
                "sample_dialogue": character.sample_dialogue,
                "avatar": character.avatar,
                "appearance_count": character.appearance_count,
                "created_at": character.created_at.isoformat() if character.created_at else None,
                "updated_at": character.updated_at.isoformat() if character.updated_at else None,
            }
        }
    except NotFoundException:
        raise
    except Exception as e:
        raise


@router.post("/update/{character_id}", summary="更新人物")
def update_character(
    character_id: int,
    character_update: CharacterUpdate,
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    """更新人物信息"""
    try:
        character = db.query(Character).filter(
            Character.id == character_id
        ).first()

        if not character:
            raise NotFoundException(f"人物 {character_id} 不存在")

        # 更新人物信息
        update_data = character_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(character, field, value)

        db.commit()
        db.refresh(character)

        logger.info(f"更新人物成功: {character.name} (ID: {character_id})")

        return {
            "code": 200,
            "message": "更新成功",
            "data": {
                "id": character.id,
                "project_id": character.project_id,
                "name": character.name,
                "age": character.age,
                "gender": character.gender,
                "appearance": character.appearance,
                "identity": character.identity,
                "hometown": character.hometown,
                "role": character.role.value if hasattr(character.role, 'value') else str(character.role),
                "personality": character.personality,
                "core_motivation": character.core_motivation,
                "fears": character.fears,
                "desires": character.desires,
                "initial_state": character.initial_state,
                "turning_point": character.turning_point,
                "final_state": character.final_state,
                "speech_style": character.speech_style,
                "sample_dialogue": character.sample_dialogue,
                "avatar": character.avatar,
                "appearance_count": character.appearance_count,
                "created_at": character.created_at.isoformat() if character.created_at else None,
                "updated_at": character.updated_at.isoformat() if character.updated_at else None,
            }
        }
    except NotFoundException:
        raise
    except ValueError as e:
        raise BusinessException(str(e))
    except Exception as e:
        raise


@router.post("/del/{character_id}", summary="删除人物")
def delete_character(character_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    """删除人物"""
    try:
        character = db.query(Character).filter(
            Character.id == character_id
        ).first()

        if not character:
            raise NotFoundException(f"人物 {character_id} 不存在")

        character_name = character.name
        db.delete(character)
        db.commit()

        logger.info(f"删除人物成功: {character_name} (ID: {character_id})")

        return {
            "code": 200,
            "message": "删除成功",
            "data": None
        }
    except NotFoundException:
        raise
    except Exception as e:
        raise
