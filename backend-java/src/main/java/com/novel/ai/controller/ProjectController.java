package com.novel.ai.controller;

import com.novel.ai.model.dto.request.ProjectCreateRequest;
import com.novel.ai.model.dto.request.ProjectUpdateRequest;
import com.novel.ai.model.dto.response.ApiResponse;
import com.novel.ai.model.dto.response.ProjectResponse;
import com.novel.ai.service.ProjectService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/projects")
public class ProjectController {

    private final ProjectService projectService;

    public ProjectController(ProjectService projectService) {
        this.projectService = projectService;
    }

    /**
     * 创建新项目
     * POST /api/projects/create
     */
    @PostMapping("/create")
    public ApiResponse<ProjectResponse> createProject(@RequestBody @Valid ProjectCreateRequest request,
                                                      HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        ProjectResponse response = projectService.createProject(userId, request);
        return ApiResponse.success("项目创建成功", response);
    }

    /**
     * 获取项目详情
     * GET /api/projects/detail/{id}
     */
    @GetMapping("/detail/{id}")
    public ApiResponse<ProjectResponse> getProjectDetail(@PathVariable Integer id,
                                                         HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        ProjectResponse response = projectService.getProjectById(id, userId);
        return ApiResponse.success(response);
    }

    /**
     * 获取用户的所有项目
     * GET /api/projects/list
     */
    @GetMapping("/list")
    public ApiResponse<List<ProjectResponse>> getProjectList(HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        List<ProjectResponse> projects = projectService.getProjectsByUserId(userId);
        return ApiResponse.success(projects);
    }

    /**
     * 根据状态获取用户的项目
     * GET /api/projects/list?status=draft
     */
    @GetMapping("/list/{status}")
    public ApiResponse<List<ProjectResponse>> getProjectListByStatus(@PathVariable String status,
                                                                     HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        List<ProjectResponse> projects = projectService.getProjectsByUserIdAndStatus(userId, status);
        return ApiResponse.success(projects);
    }

    /**
     * 更新项目信息
     * POST /api/projects/update/{id}
     */
    @PostMapping("/update/{id}")
    public ApiResponse<ProjectResponse> updateProject(@PathVariable Integer id,
                                                     @RequestBody @Valid ProjectUpdateRequest request,
                                                     HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        ProjectResponse response = projectService.updateProject(id, userId, request);
        return ApiResponse.success("项目更新成功", response);
    }

    /**
     * 删除项目
     * POST /api/projects/del/{id}
     */
    @PostMapping("/del/{id}")
    public ApiResponse<String> deleteProject(@PathVariable Integer id,
                                           HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        projectService.deleteProject(id, userId);
        return ApiResponse.success("项目删除成功");
    }
}