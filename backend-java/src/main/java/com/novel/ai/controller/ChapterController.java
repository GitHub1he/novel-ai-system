package com.novel.ai.controller;

import com.novel.ai.model.dto.request.ChapterCreateRequest;
import com.novel.ai.model.dto.request.ChapterUpdateRequest;
import com.novel.ai.model.dto.response.ApiResponse;
import com.novel.ai.model.dto.response.ChapterResponse;
import com.novel.ai.service.ChapterService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/chapters")
public class ChapterController {

    private final ChapterService chapterService;

    public ChapterController(ChapterService chapterService) {
        this.chapterService = chapterService;
    }

    /**
     * 创建新章节
     * POST /api/chapters/
     */
    @PostMapping("/")
    public ApiResponse<ChapterResponse> createChapter(@RequestBody @Valid ChapterCreateRequest request,
                                                      HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        ChapterResponse response = chapterService.createChapter(userId, request);
        return ApiResponse.success("创建成功", response);
    }

    /**
     * 获取章节详情
     * GET /api/chapters/{chapter_id}
     */
    @GetMapping("/{chapter_id}")
    public ApiResponse<ChapterResponse> getChapterDetail(@PathVariable("chapter_id") Integer chapterId,
                                                         HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        ChapterResponse response = chapterService.getChapterById(chapterId, userId);
        return ApiResponse.success("获取成功", response);
    }

    /**
     * 获取项目的章节列表
     * GET /api/chapters/list/{project_id}
     */
    @GetMapping("/list/{project_id}")
    public ApiResponse<List<ChapterResponse>> getChapterList(@PathVariable("project_id") Integer projectId,
                                                            HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        List<ChapterResponse> chapters = chapterService.getChaptersByProjectId(projectId, userId);
        return ApiResponse.success(chapters);
    }

    /**
     * 根据状态获取项目的章节
     * GET /api/chapters/list/{project_id}/{status}
     */
    @GetMapping("/list/{project_id}/{status}")
    public ApiResponse<List<ChapterResponse>> getChapterListByStatus(
            @PathVariable("project_id") Integer projectId,
            @PathVariable String status,
            HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        List<ChapterResponse> chapters = chapterService.getChaptersByProjectIdAndStatus(projectId, status, userId);
        return ApiResponse.success(chapters);
    }

    /**
     * 更新章节信息
     * PUT /api/chapters/{chapter_id}
     */
    @PutMapping("/{chapter_id}")
    public ApiResponse<ChapterResponse> updateChapter(@PathVariable("chapter_id") Integer chapterId,
                                                     @RequestBody @Valid ChapterUpdateRequest request,
                                                     HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        ChapterResponse response = chapterService.updateChapter(chapterId, userId, request);
        return ApiResponse.success("更新成功", response);
    }

    /**
     * 删除章节
     * DELETE /api/chapters/{chapter_id}
     */
    @DeleteMapping("/{chapter_id}")
    public ApiResponse<String> deleteChapter(@PathVariable("chapter_id") Integer chapterId,
                                           HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        chapterService.deleteChapter(chapterId, userId);
        return ApiResponse.success("删除成功");
    }

    /**
     * 获取下一个章节号
     * GET /api/chapters/next-number/{project_id}
     */
    @GetMapping("/next-number/{project_id}")
    public ApiResponse<Integer> getNextChapterNumber(@PathVariable("project_id") Integer projectId,
                                                    HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        Integer nextNumber = chapterService.getNextChapterNumber(projectId, userId);
        return ApiResponse.success(nextNumber);
    }
}