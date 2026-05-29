package com.novel.ai.controller;

import com.novel.ai.model.dto.request.PlotNodeCreateRequest;
import com.novel.ai.model.dto.request.PlotNodeUpdateRequest;
import com.novel.ai.model.dto.response.ApiResponse;
import com.novel.ai.model.dto.response.PlotNodeResponse;
import com.novel.ai.service.PlotNodeService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 情节节点管理控制器
 * 提供情节节点CRUD操作的REST API接口
 */
@RestController
@RequestMapping("/api/plot-nodes")
public class PlotNodeController {

    private final PlotNodeService plotNodeService;

    public PlotNodeController(PlotNodeService plotNodeService) {
        this.plotNodeService = plotNodeService;
    }

    /**
     * 创建新情节节点
     * POST /api/plot-nodes/
     */
    @PostMapping("/")
    public ApiResponse<PlotNodeResponse> createPlotNode(@RequestBody @Valid PlotNodeCreateRequest request,
                                                          HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        PlotNodeResponse response = plotNodeService.createPlotNode(userId, request);
        return ApiResponse.success("创建成功", response);
    }

    /**
     * 获取情节节点详情
     * GET /api/plot-nodes/{plot_node_id}
     */
    @GetMapping("/{plot_node_id}")
    public ApiResponse<PlotNodeResponse> getPlotNodeDetail(@PathVariable("plot_node_id") Integer plotNodeId,
                                                            HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        PlotNodeResponse response = plotNodeService.getPlotNodeById(plotNodeId, userId);
        return ApiResponse.success("获取成功", response);
    }

    /**
     * 获取项目的所有情节节点
     * GET /api/plot-nodes/list/{project_id}
     */
    @GetMapping("/list/{project_id}")
    public ApiResponse<List<PlotNodeResponse>> getPlotNodeList(@PathVariable("project_id") Integer projectId,
                                                              HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        List<PlotNodeResponse> plotNodes = plotNodeService.getPlotNodesByProjectId(projectId, userId);
        return ApiResponse.success(plotNodes);
    }

    /**
     * 根据重要程度获取项目的情节节点
     * GET /api/plot-nodes/list/{project_id}/{importance}
     */
    @GetMapping("/list/{project_id}/{importance}")
    public ApiResponse<List<PlotNodeResponse>> getPlotNodeListByImportance(
            @PathVariable("project_id") Integer projectId,
            @PathVariable("importance") String importance,
            HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        List<PlotNodeResponse> plotNodes = plotNodeService.getPlotNodesByProjectIdAndImportance(projectId, importance, userId);
        return ApiResponse.success(plotNodes);
    }

    /**
     * 根据情节类型获取项目的情节节点
     * GET /api/plot-nodes/by-type/{project_id}/{plot_type}
     */
    @GetMapping("/by-type/{project_id}/{plot_type}")
    public ApiResponse<List<PlotNodeResponse>> getPlotNodeListByType(
            @PathVariable("project_id") Integer projectId,
            @PathVariable("plot_type") String plotType,
            HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        List<PlotNodeResponse> plotNodes = plotNodeService.getPlotNodesByProjectIdAndType(projectId, plotType, userId);
        return ApiResponse.success(plotNodes);
    }

    /**
     * 根据章节ID获取情节节点
     * GET /api/plot-nodes/by-chapter/{chapter_id}
     */
    @GetMapping("/by-chapter/{chapter_id}")
    public ApiResponse<List<PlotNodeResponse>> getPlotNodeListByChapter(
            @PathVariable("chapter_id") Integer chapterId,
            HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        List<PlotNodeResponse> plotNodes = plotNodeService.getPlotNodesByChapterId(chapterId, userId);
        return ApiResponse.success(plotNodes);
    }

    /**
     * 获取项目的主线情节
     * GET /api/plot-nodes/main-plots/{project_id}
     */
    @GetMapping("/main-plots/{project_id}")
    public ApiResponse<List<PlotNodeResponse>> getMainPlots(@PathVariable("project_id") Integer projectId,
                                                             HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        List<PlotNodeResponse> plotNodes = plotNodeService.getMainPlots(projectId, userId);
        return ApiResponse.success(plotNodes);
    }

    /**
     * 获取项目的高潮情节
     * GET /api/plot-nodes/climax-plots/{project_id}
     */
    @GetMapping("/climax-plots/{project_id}")
    public ApiResponse<List<PlotNodeResponse>> getClimaxPlots(@PathVariable("project_id") Integer projectId,
                                                               HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        List<PlotNodeResponse> plotNodes = plotNodeService.getClimaxPlots(projectId, userId);
        return ApiResponse.success(plotNodes);
    }

    /**
     * 更新情节节点
     * PUT /api/plot-nodes/{plot_node_id}
     */
    @PutMapping("/{plot_node_id}")
    public ApiResponse<PlotNodeResponse> updatePlotNode(@PathVariable("plot_node_id") Integer plotNodeId,
                                                         @RequestBody @Valid PlotNodeUpdateRequest request,
                                                         HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        PlotNodeResponse response = plotNodeService.updatePlotNode(plotNodeId, userId, request);
        return ApiResponse.success("更新成功", response);
    }

    /**
     * 删除情节节点
     * DELETE /api/plot-nodes/{plot_node_id}
     */
    @DeleteMapping("/{plot_node_id}")
    public ApiResponse<String> deletePlotNode(@PathVariable("plot_node_id") Integer plotNodeId,
                                             HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        plotNodeService.deletePlotNode(plotNodeId, userId);
        return ApiResponse.success("删除成功");
    }

    /**
     * 统计项目的情节节点数量
     * GET /api/plot-nodes/count/{project_id}
     */
    @GetMapping("/count/{project_id}")
    public ApiResponse<Integer> countPlotNodes(@PathVariable("project_id") Integer projectId,
                                               HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        int count = plotNodeService.countPlotNodes(projectId, userId);
        return ApiResponse.success(count);
    }
}
