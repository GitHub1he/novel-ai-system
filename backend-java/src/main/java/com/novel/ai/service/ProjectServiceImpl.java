package com.novel.ai.service;

import com.novel.ai.exception.BusinessException;
import com.novel.ai.exception.NotFoundException;
import com.novel.ai.mapper.ProjectMapper;
import com.novel.ai.model.dto.request.ProjectCreateRequest;
import com.novel.ai.model.dto.request.ProjectUpdateRequest;
import com.novel.ai.model.dto.response.ProjectResponse;
import com.novel.ai.model.entity.Project;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class ProjectServiceImpl implements ProjectService {

    private final ProjectMapper projectMapper;

    public ProjectServiceImpl(ProjectMapper projectMapper) {
        this.projectMapper = projectMapper;
    }

    @Override
    public ProjectResponse createProject(Integer userId, ProjectCreateRequest request) {
        // 验证用户输入
        validateProjectRequest(request);

        // 创建项目实体
        Project project = new Project(userId, request.getTitle(), request.getAuthor());

        // 设置可选字段
        if (request.getGenre() != null) {
            project.setGenre(request.getGenre());
        }
        if (request.getTags() != null) {
            project.setTags(request.getTags());
        }
        if (request.getSummary() != null) {
            project.setSummary(request.getSummary());
        }
        if (request.getTargetReaders() != null) {
            project.setTargetReaders(request.getTargetReaders());
        }
        if (request.getDefaultPov() != null) {
            project.setDefaultPov(request.getDefaultPov());
        }
        if (request.getStyle() != null) {
            project.setStyle(request.getStyle());
        }
        if (request.getStyleKeywords() != null) {
            project.setStyleKeywords(request.getStyleKeywords());
        }
        if (request.getLanguageStyle() != null) {
            project.setLanguageStyle(request.getLanguageStyle());
        }
        if (request.getSensoryFocus() != null) {
            project.setSensoryFocus(request.getSensoryFocus());
        }
        if (request.getStyleIntensity() != null && request.getStyleIntensity() >= 0 && request.getStyleIntensity() <= 100) {
            project.setStyleIntensity(request.getStyleIntensity());
        }
        if (request.getTargetWordsPerChapter() != null && request.getTargetWordsPerChapter() > 0) {
            project.setTargetWordsPerChapter(request.getTargetWordsPerChapter());
        }
        if (request.getBackgroundTemplate() != null) {
            project.setBackgroundTemplate(request.getBackgroundTemplate());
        }

        project.setCreatedAt(LocalDateTime.now());
        project.setUpdatedAt(LocalDateTime.now());

        // 保存到数据库
        int result = projectMapper.insert(project);

        if (result <= 0) {
            throw new BusinessException("项目创建失败");
        }

        return convertToResponse(project);
    }

    @Override
    public ProjectResponse getProjectById(Integer projectId, Integer userId) {
        Project project = projectMapper.findById(projectId);

        if (project == null) {
            throw new NotFoundException("项目不存在");
        }

        // 验证权限：只能访问自己的项目
        if (!project.getUserId().equals(userId)) {
            throw new BusinessException("无权访问该项目");
        }

        return convertToResponse(project);
    }

    @Override
    public List<ProjectResponse> getProjectsByUserId(Integer userId) {
        List<Project> projects = projectMapper.findByUserId(userId);
        return projects.stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }

    @Override
    public List<ProjectResponse> getProjectsByUserIdAndStatus(Integer userId, String status) {
        List<Project> projects = projectMapper.findByUserIdAndStatus(userId, status);
        return projects.stream()
                .map(this::convertToResponse)
                .collect(Collectors.toList());
    }

    @Override
    public ProjectResponse updateProject(Integer projectId, Integer userId, ProjectUpdateRequest request) {
        // 验证用户输入
        validateProjectRequest(request);

        // 获取现有项目
        Project existingProject = projectMapper.findById(projectId);
        if (existingProject == null) {
            throw new NotFoundException("项目不存在");
        }

        // 验证权限：只能修改自己的项目
        if (!existingProject.getUserId().equals(userId)) {
            throw new BusinessException("无权修改该项目");
        }

        // 更新项目信息
        existingProject.setTitle(request.getTitle());
        existingProject.setAuthor(request.getAuthor());
        existingProject.setGenre(request.getGenre());
        existingProject.setTags(request.getTags());
        existingProject.setSummary(request.getSummary());
        existingProject.setTargetReaders(request.getTargetReaders());

        if (request.getStatus() != null) {
            existingProject.setStatus(request.getStatus());
        }
        if (request.getDefaultPov() != null) {
            existingProject.setDefaultPov(request.getDefaultPov());
        }
        if (request.getStyle() != null) {
            existingProject.setStyle(request.getStyle());
        }
        if (request.getStyleKeywords() != null) {
            existingProject.setStyleKeywords(request.getStyleKeywords());
        }
        if (request.getLanguageStyle() != null) {
            existingProject.setLanguageStyle(request.getLanguageStyle());
        }
        if (request.getSensoryFocus() != null) {
            existingProject.setSensoryFocus(request.getSensoryFocus());
        }
        if (request.getStyleIntensity() != null) {
            existingProject.setStyleIntensity(request.getStyleIntensity());
        }
        if (request.getTargetWordsPerChapter() != null) {
            existingProject.setTargetWordsPerChapter(request.getTargetWordsPerChapter());
        }
        if (request.getBackgroundTemplate() != null) {
            existingProject.setBackgroundTemplate(request.getBackgroundTemplate());
        }

        existingProject.setUpdatedAt(LocalDateTime.now());

        // 保存更新
        int result = projectMapper.update(existingProject);

        if (result <= 0) {
            throw new BusinessException("项目更新失败");
        }

        return convertToResponse(existingProject);
    }

    @Override
    public void deleteProject(Integer projectId, Integer userId) {
        // 获取现有项目
        Project existingProject = projectMapper.findById(projectId);
        if (existingProject == null) {
            throw new NotFoundException("项目不存在");
        }

        // 验证权限：只能删除自己的项目
        if (!existingProject.getUserId().equals(userId)) {
            throw new BusinessException("无权删除该项目");
        }

        // 删除项目
        int result = projectMapper.delete(projectId);

        if (result <= 0) {
            throw new BusinessException("项目删除失败");
        }
    }

    @Override
    public void updateProjectStatistics(Integer projectId, Integer totalWords, Integer totalChapters) {
        Project project = projectMapper.findById(projectId);
        if (project == null) {
            throw new NotFoundException("项目不存在");
        }

        project.setTotalWords(totalWords);
        project.setTotalChapters(totalChapters);

        // 计算完成度（基于目标字数和章节数）
        if (project.getTargetWordsPerChapter() != null && project.getTargetWordsPerChapter() > 0) {
            int targetTotalWords = project.getTargetWordsPerChapter() * totalChapters;
            if (targetTotalWords > 0) {
                int completionRate = (int) ((totalWords * 100.0) / targetTotalWords);
                project.setCompletionRate(Math.min(completionRate, 100)); // 最大100%
            }
        }

        project.setUpdatedAt(LocalDateTime.now());

        projectMapper.updateStatistics(project);
    }

    /**
     * 验证项目请求参数
     */
    private void validateProjectRequest(Object request) {
        // 基本验证由 @Valid 注解处理
        // 这里可以添加额外的业务逻辑验证
    }

    /**
     * 将Project实体转换为ProjectResponse
     */
    private ProjectResponse convertToResponse(Project project) {
        ProjectResponse response = new ProjectResponse();
        response.setId(project.getId());
        response.setUserId(project.getUserId());
        response.setTitle(project.getTitle());
        response.setAuthor(project.getAuthor());
        response.setGenre(project.getGenre());
        response.setTags(project.getTags());
        response.setSummary(project.getSummary());
        response.setTargetReaders(project.getTargetReaders());
        response.setStatus(project.getStatus());
        response.setDefaultPov(project.getDefaultPov());
        response.setStyle(project.getStyle());
        response.setStyleKeywords(project.getStyleKeywords());
        response.setLanguageStyle(project.getLanguageStyle());
        response.setSensoryFocus(project.getSensoryFocus());
        response.setStyleIntensity(project.getStyleIntensity());
        response.setTargetWordsPerChapter(project.getTargetWordsPerChapter());
        response.setBackgroundTemplate(project.getBackgroundTemplate());
        response.setTotalWords(project.getTotalWords());
        response.setTotalChapters(project.getTotalChapters());
        response.setCompletionRate(project.getCompletionRate());
        response.setCreatedAt(project.getCreatedAt());
        response.setUpdatedAt(project.getUpdatedAt());
        return response;
    }
}