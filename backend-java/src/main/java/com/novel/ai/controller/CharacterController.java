package com.novel.ai.controller;

import com.novel.ai.model.dto.request.CharacterCreateRequest;
import com.novel.ai.model.dto.request.CharacterUpdateRequest;
import com.novel.ai.model.dto.response.ApiResponse;
import com.novel.ai.model.dto.response.CharacterResponse;
import com.novel.ai.service.CharacterService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 人物管理控制器
 * 提供人物CRUD操作的REST API接口
 */
@RestController
@RequestMapping("/api/characters")
public class CharacterController {

    private final CharacterService characterService;

    public CharacterController(CharacterService characterService) {
        this.characterService = characterService;
    }

    /**
     * 创建新人物
     * POST /api/characters/
     */
    @PostMapping("/")
    public ApiResponse<CharacterResponse> createCharacter(@RequestBody @Valid CharacterCreateRequest request,
                                                           HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        CharacterResponse response = characterService.createCharacter(userId, request);
        return ApiResponse.success("创建成功", response);
    }

    /**
     * 获取人物详情
     * GET /api/characters/{character_id}
     */
    @GetMapping("/{character_id}")
    public ApiResponse<CharacterResponse> getCharacterDetail(@PathVariable("character_id") Integer characterId,
                                                              HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        CharacterResponse response = characterService.getCharacterById(characterId, userId);
        return ApiResponse.success("获取成功", response);
    }

    /**
     * 获取项目的所有人物
     * GET /api/characters/list/{project_id}
     */
    @GetMapping("/list/{project_id}")
    public ApiResponse<List<CharacterResponse>> getCharacterList(@PathVariable("project_id") Integer projectId,
                                                                 HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        List<CharacterResponse> characters = characterService.getCharactersByProjectId(projectId, userId);
        return ApiResponse.success(characters);
    }

    /**
     * 根据角色类型获取项目的人物
     * GET /api/characters/list/{project_id}/{role}
     */
    @GetMapping("/list/{project_id}/{role}")
    public ApiResponse<List<CharacterResponse>> getCharacterListByRole(
            @PathVariable("project_id") Integer projectId,
            @PathVariable("role") String role,
            HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        List<CharacterResponse> characters = characterService.getCharactersByProjectIdAndRole(projectId, role, userId);
        return ApiResponse.success(characters);
    }

    /**
     * 获取项目的主角列表
     * GET /api/characters/protagonists/{project_id}
     */
    @GetMapping("/protagonists/{project_id}")
    public ApiResponse<List<CharacterResponse>> getProtagonists(@PathVariable("project_id") Integer projectId,
                                                                HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        List<CharacterResponse> characters = characterService.getProtagonists(projectId, userId);
        return ApiResponse.success(characters);
    }

    /**
     * 获取项目的反派列表
     * GET /api/characters/antagonists/{project_id}
     */
    @GetMapping("/antagonists/{project_id}")
    public ApiResponse<List<CharacterResponse>> getAntagonists(@PathVariable("project_id") Integer projectId,
                                                               HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        List<CharacterResponse> characters = characterService.getAntagonists(projectId, userId);
        return ApiResponse.success(characters);
    }

    /**
     * 更新人物信息
     * PUT /api/characters/{character_id}
     */
    @PutMapping("/{character_id}")
    public ApiResponse<CharacterResponse> updateCharacter(@PathVariable("character_id") Integer characterId,
                                                         @RequestBody @Valid CharacterUpdateRequest request,
                                                         HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        CharacterResponse response = characterService.updateCharacter(characterId, userId, request);
        return ApiResponse.success("更新成功", response);
    }

    /**
     * 删除人物
     * DELETE /api/characters/{character_id}
     */
    @DeleteMapping("/{character_id}")
    public ApiResponse<String> deleteCharacter(@PathVariable("character_id") Integer characterId,
                                              HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        characterService.deleteCharacter(characterId, userId);
        return ApiResponse.success("删除成功");
    }

    /**
     * 统计项目的人物数量
     * GET /api/characters/count/{project_id}
     */
    @GetMapping("/count/{project_id}")
    public ApiResponse<Integer> countCharacters(@PathVariable("project_id") Integer projectId,
                                               HttpServletRequest httpRequest) {
        Integer userId = (Integer) httpRequest.getAttribute("userId");
        int count = characterService.countCharacters(projectId, userId);
        return ApiResponse.success(count);
    }
}