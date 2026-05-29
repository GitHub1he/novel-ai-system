package com.novel.ai.controller;

import com.novel.ai.model.dto.request.WorldSettingCreateRequest;
import com.novel.ai.model.dto.request.WorldSettingUpdateRequest;
import com.novel.ai.model.dto.response.ApiResponse;
import com.novel.ai.model.dto.response.WorldSettingResponse;
import com.novel.ai.service.WorldSettingService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 世界观设定管理控制器
 * 提供世界观设定CRUD操作的REST API接口
 */
@RestController
@RequestMapping("/api/world-settings")
public class WorldSettingController {

    private final WorldSettingService worldSettingService;

    public WorldSettingController(WorldSettingService worldSettingService) {
        this.worldSettingService = worldSettingService;
    }

    /**
     * 创建新世界观设定
     * POST /api/world-settings/
     */
    @PostMapping("/")
    public ApiResponse<WorldSettingResponse> createWorldSetting(@RequestBody @Valid WorldSettingCreateRequest request,
                                                                  HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        WorldSettingResponse response = worldSettingService.createWorldSetting(userId, request);
        return ApiResponse.success("创建成功", response);
    }

    /**
     * 获取世界观设定详情
     * GET /api/world-settings/{world_setting_id}
     */
    @GetMapping("/{world_setting_id}")
    public ApiResponse<WorldSettingResponse> getWorldSettingDetail(@PathVariable("world_setting_id") Integer worldSettingId,
                                                                    HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        WorldSettingResponse response = worldSettingService.getWorldSettingById(worldSettingId, userId);
        return ApiResponse.success("获取成功", response);
    }

    /**
     * 获取项目的所有世界观设定
     * GET /api/world-settings/list/{project_id}
     */
    @GetMapping("/list/{project_id}")
    public ApiResponse<List<WorldSettingResponse>> getWorldSettingList(@PathVariable("project_id") Integer projectId,
                                                                       HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        List<WorldSettingResponse> worldSettings = worldSettingService.getWorldSettingsByProjectId(projectId, userId);
        return ApiResponse.success(worldSettings);
    }

    /**
     * 根据设定类型获取项目的世界观设定
     * GET /api/world-settings/list/{project_id}/{setting_type}
     */
    @GetMapping("/list/{project_id}/{setting_type}")
    public ApiResponse<List<WorldSettingResponse>> getWorldSettingListByType(
            @PathVariable("project_id") Integer projectId,
            @PathVariable("setting_type") String settingType,
            HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        List<WorldSettingResponse> worldSettings = worldSettingService.getWorldSettingsByProjectIdAndType(
                projectId, settingType, userId);
        return ApiResponse.success(worldSettings);
    }

    /**
     * 获取项目的核心规则
     * GET /api/world-settings/core-rules/{project_id}
     */
    @GetMapping("/core-rules/{project_id}")
    public ApiResponse<List<WorldSettingResponse>> getCoreRules(@PathVariable("project_id") Integer projectId,
                                                                HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        List<WorldSettingResponse> worldSettings = worldSettingService.getCoreRules(projectId, userId);
        return ApiResponse.success(worldSettings);
    }

    /**
     * 更新世界观设定
     * PUT /api/world-settings/{world_setting_id}
     */
    @PutMapping("/{world_setting_id}")
    public ApiResponse<WorldSettingResponse> updateWorldSetting(@PathVariable("world_setting_id") Integer worldSettingId,
                                                                @RequestBody @Valid WorldSettingUpdateRequest request,
                                                                HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        WorldSettingResponse response = worldSettingService.updateWorldSetting(worldSettingId, userId, request);
        return ApiResponse.success("更新成功", response);
    }

    /**
     * 删除世界观设定
     * DELETE /api/world-settings/{world_setting_id}
     */
    @DeleteMapping("/{world_setting_id}")
    public ApiResponse<String> deleteWorldSetting(@PathVariable("world_setting_id") Integer worldSettingId,
                                                   HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        worldSettingService.deleteWorldSetting(worldSettingId, userId);
        return ApiResponse.success("删除成功");
    }

    /**
     * 统计项目的世界观设定数量
     * GET /api/world-settings/count/{project_id}
     */
    @GetMapping("/count/{project_id}")
    public ApiResponse<Integer> countWorldSettings(@PathVariable("project_id") Integer projectId,
                                                    HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        int count = worldSettingService.countWorldSettings(projectId, userId);
        return ApiResponse.success(count);
    }
}