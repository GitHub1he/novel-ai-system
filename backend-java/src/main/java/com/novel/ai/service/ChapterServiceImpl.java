package com.novel.ai.service;

import com.novel.ai.exception.BusinessException;
import com.novel.ai.exception.NotFoundException;
import com.novel.ai.mapper.ChapterMapper;
import com.novel.ai.mapper.ProjectMapper;
import com.novel.ai.model.dto.request.ChapterCreateRequest;
import com.novel.ai.model.dto.request.ChapterUpdateRequest;
import com.novel.ai.model.dto.response.ChapterResponse;
import com.novel.ai.model.entity.Chapter;
import com.novel.ai.model.entity.Project;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class ChapterServiceImpl implements ChapterService {

    private final ChapterMapper chapterMapper;
    private final ProjectMapper projectMapper;

    public ChapterServiceImpl(ChapterMapper chapterMapper, ProjectMapper projectMapper) {
        this.chapterMapper = chapterMapper;
        this.projectMapper = projectMapper;
    }

    @Override
    public ChapterResponse createChapter(Integer userId, ChapterCreateRequest request) {
        // 验证项目权限
        Project project = projectMapper.findById(request.getProjectId());
        if (project == null) {
            throw new NotFoundException("项目不存在");
        }
        if (!project.getUserId().equals(userId)) {
            throw new BusinessException("无权在该项目中创建章节");
        }

        // 检查章节号是否已存在
        int existingCount = chapterMapper.countByProjectIdAndChapterNumber(
                request.getProjectId(), request.getChapterNumber());
        if (existingCount > 0) {
            throw new BusinessException("该章节号已存在");
        }

        // 创建章节实体
        Chapter chapter = new Chapter(request.getProjectId(), request.getChapterNumber(), request.getTitle());

        // 设置可选字段
        if (request.getVolume() != null) {
            chapter.setVolume(request.getVolume());
        }
        if (request.getOutline() != null) {
            chapter.setOutline(request.getOutline());
        }
        if (request.getSummary() != null) {
            chapter.setSummary(request.getSummary());
        }
        if (request.getDisplaySummary() != null) {
            chapter.setDisplaySummary(request.getDisplaySummary());
        }
        if (request.getPovCharacterId() != null) {
            chapter.setPovCharacterId(request.getPovCharacterId());
        }
        if (request.getFeaturedCharacters() != null) {
            chapter.setFeaturedCharacters(request.getFeaturedCharacters());
        }
        if (request.getLocations() != null) {
            chapter.setLocations(request.getLocations());
        }

        chapter.setCreatedAt(LocalDateTime.now());
        chapter.setUpdatedAt(LocalDateTime.now());

        // 保存到数据库
        int result = chapterMapper.insert(chapter);

        if (result <= 0) {
            throw new BusinessException("章节创建失败");
        }

        return convertToResponse(chapter);
    }

    @Override
    public ChapterResponse getChapterById(Integer chapterId, Integer userId) {
        Chapter chapter = chapterMapper.findById(chapterId);

        if (chapter == null) {
            throw new NotFoundException("章节不存在");
        }

        // 验证权限：只能访问自己项目的章节
        Project project = projectMapper.findById(chapter.getProjectId());
        if (project == null || !project.getUserId().equals(userId)) {
            throw new BusinessException("无权访问该章节");
        }

        return convertToResponse(chapter);
    }

    @Override
    public List<ChapterResponse> getChaptersByProjectId(Integer projectId, Integer userId) {
        // 验证项目权限
        Project project = projectMapper.findById(projectId);
        if (project == null) {
            throw new NotFoundException("项目不存在");
        }
        if (!project.getUserId().equals(userId)) {
            throw new BusinessException("无权访问该项目的章节");
        }

        List<Chapter> chapters = chapterMapper.findByProjectId(projectId);

        // 对于列表视图，清空content字段以提高性能
        return chapters.stream()
                .map(chapter -> {
                    ChapterResponse response = convertToResponse(chapter);
                    response.setContent(null); // 列表不返回内容
                    return response;
                })
                .collect(Collectors.toList());
    }

    @Override
    public List<ChapterResponse> getChaptersByProjectIdAndStatus(Integer projectId, String status, Integer userId) {
        // 验证项目权限
        Project project = projectMapper.findById(projectId);
        if (project == null) {
            throw new NotFoundException("项目不存在");
        }
        if (!project.getUserId().equals(userId)) {
            throw new BusinessException("无权访问该项目的章节");
        }

        List<Chapter> chapters = chapterMapper.findByProjectIdAndStatus(projectId, status);

        // 对于列表视图，清空content字段以提高性能
        return chapters.stream()
                .map(chapter -> {
                    ChapterResponse response = convertToResponse(chapter);
                    response.setContent(null); // 列表不返回内容
                    return response;
                })
                .collect(Collectors.toList());
    }

    @Override
    public ChapterResponse updateChapter(Integer chapterId, Integer userId, ChapterUpdateRequest request) {
        // 获取现有章节
        Chapter existingChapter = chapterMapper.findById(chapterId);
        if (existingChapter == null) {
            throw new NotFoundException("章节不存在");
        }

        // 验证权限：只能修改自己项目的章节
        Project project = projectMapper.findById(existingChapter.getProjectId());
        if (project == null || !project.getUserId().equals(userId)) {
            throw new BusinessException("无权修改该章节");
        }

        // 更新章节信息
        existingChapter.setTitle(request.getTitle());
        if (request.getContent() != null) {
            existingChapter.setContent(request.getContent());
        }
        if (request.getOutline() != null) {
            existingChapter.setOutline(request.getOutline());
        }
        if (request.getSummary() != null) {
            existingChapter.setSummary(request.getSummary());
        }
        if (request.getDisplaySummary() != null) {
            existingChapter.setDisplaySummary(request.getDisplaySummary());
        }
        if (request.getVolume() != null) {
            existingChapter.setVolume(request.getVolume());
        }
        if (request.getPovCharacterId() != null) {
            existingChapter.setPovCharacterId(request.getPovCharacterId());
        }
        if (request.getFeaturedCharacters() != null) {
            existingChapter.setFeaturedCharacters(request.getFeaturedCharacters());
        }
        if (request.getLocations() != null) {
            existingChapter.setLocations(request.getLocations());
        }
        if (request.getStatus() != null) {
            existingChapter.setStatus(request.getStatus());
        }

        // 更新版本号
        if (request.getContent() != null) {
            existingChapter.setVersion(existingChapter.getVersion() + 1);
        }

        existingChapter.setUpdatedAt(LocalDateTime.now());

        // 保存更新
        int result = chapterMapper.update(existingChapter);

        if (result <= 0) {
            throw new BusinessException("章节更新失败");
        }

        return convertToResponse(existingChapter);
    }

    @Override
    public void deleteChapter(Integer chapterId, Integer userId) {
        // 获取现有章节
        Chapter existingChapter = chapterMapper.findById(chapterId);
        if (existingChapter == null) {
            throw new NotFoundException("章节不存在");
        }

        // 验证权限：只能删除自己项目的章节
        Project project = projectMapper.findById(existingChapter.getProjectId());
        if (project == null || !project.getUserId().equals(userId)) {
            throw new BusinessException("无权删除该章节");
        }

        // 删除章节
        int result = chapterMapper.delete(chapterId);

        if (result <= 0) {
            throw new BusinessException("章节删除失败");
        }
    }

    @Override
    public void updateChapterStatus(Integer chapterId, Integer userId, String status) {
        // 获取现有章节
        Chapter existingChapter = chapterMapper.findById(chapterId);
        if (existingChapter == null) {
            throw new NotFoundException("章节不存在");
        }

        // 验证权限：只能修改自己项目的章节
        Project project = projectMapper.findById(existingChapter.getProjectId());
        if (project == null || !project.getUserId().equals(userId)) {
            throw new BusinessException("无权修改该章节");
        }

        existingChapter.setStatus(status);
        existingChapter.setUpdatedAt(LocalDateTime.now());

        int result = chapterMapper.updateStatus(existingChapter);

        if (result <= 0) {
            throw new BusinessException("章节状态更新失败");
        }
    }

    @Override
    public Integer getNextChapterNumber(Integer projectId, Integer userId) {
        // 验证项目权限
        Project project = projectMapper.findById(projectId);
        if (project == null) {
            throw new NotFoundException("项目不存在");
        }
        if (!project.getUserId().equals(userId)) {
            throw new BusinessException("无权访问该项目");
        }

        Integer maxChapterNumber = chapterMapper.findMaxChapterNumberByProjectId(projectId);
        return maxChapterNumber == null ? 1 : maxChapterNumber + 1;
    }

    /**
     * 将Chapter实体转换为ChapterResponse
     */
    private ChapterResponse convertToResponse(Chapter chapter) {
        ChapterResponse response = new ChapterResponse();
        response.setId(chapter.getId());
        response.setProjectId(chapter.getProjectId());
        response.setChapterNumber(chapter.getChapterNumber());
        response.setTitle(chapter.getTitle());
        response.setVolume(chapter.getVolume());
        response.setContent(chapter.getContent());
        response.setOutline(chapter.getOutline());
        response.setSummary(chapter.getSummary());
        response.setDisplaySummary(chapter.getDisplaySummary());
        response.setPovCharacterId(chapter.getPovCharacterId());
        response.setFeaturedCharacters(chapter.getFeaturedCharacters());
        response.setLocations(chapter.getLocations());
        response.setStatus(chapter.getStatus());
        response.setWordCount(chapter.getWordCount());
        response.setVersion(chapter.getVersion());
        response.setCreatedAt(chapter.getCreatedAt());
        response.setUpdatedAt(chapter.getUpdatedAt());
        return response;
    }
}