from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.chapter import Chapter
from app.models.project import Project
from app.services.ai_service import ai_service

router = APIRouter(prefix="/chapters", tags=["章节管理"])


@router.post("/", summary="创建章节")
def create_chapter(
    project_id: int,
    title: str,
    chapter_number: int,
    db: Session = Depends(get_db)
):
    """创建新章节"""
    # 验证项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )

    chapter = Chapter(
        project_id=project_id,
        title=title,
        chapter_number=chapter_number
    )
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    return chapter


@router.get("/{chapter_id}", summary="获取章节详情")
def get_chapter(chapter_id: int, db: Session = Depends(get_db)):
    """获取章节详情"""
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不存在"
        )
    return chapter


@router.put("/{chapter_id}", summary="更新章节")
def update_chapter(
    chapter_id: int,
    title: Optional[str] = None,
    content: Optional[str] = None,
    outline: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """更新章节内容"""
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不存在"
        )

    if title is not None:
        chapter.title = title
    if content is not None:
        chapter.content = content
        # 更新字数统计
        chapter.word_count = len(content)
    if outline is not None:
        chapter.outline = outline

    db.commit()
    db.refresh(chapter)
    return chapter


@router.post("/{chapter_id}/generate", summary="AI生成章节内容")
def generate_chapter_content(
    chapter_id: int,
    prompt: str,
    db: Session = Depends(get_db)
):
    """使用AI生成章节内容"""
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不存在"
        )

    project = db.query(Project).filter(Project.id == chapter.project_id).first()

    # TODO: 构建上下文（人物、世界观设定）
    context = ai_service._build_context(
        project_data={
            "title": project.title,
            "genre": project.genre,
            "summary": project.summary,
            "style": project.style
        },
        characters=[],
        world_settings=[]
    )

    # 生成内容
    try:
        content = ai_service.generate_chapter(
            prompt=prompt,
            context=context,
            word_count=project.target_words_per_chapter,
            style=project.style
        )

        # 保存生成的内容
        chapter.content = content
        chapter.word_count = len(content)
        db.commit()

        return {"content": content, "word_count": len(content)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
