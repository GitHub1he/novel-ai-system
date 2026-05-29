package com.novel.ai.mapper;

import com.novel.ai.model.entity.PlotNode;
import org.apache.ibatis.annotations.*;

import java.util.List;

/**
 * 情节节点数据库访问接口
 * 使用MyBatis注解实现数据库操作
 */
@Mapper
public interface PlotNodeMapper {

    /**
     * 插入新情节节点
     */
    @Insert("INSERT INTO plot_nodes (project_id, title, description, plot_type, importance, " +
            "chapter_id, related_characters, related_locations, related_world_settings, " +
            "conflict_points, theme_tags, created_at, updated_at) " +
            "VALUES (#{projectId}, #{title}, #{description}, #{plotType}, #{importance}, " +
            "#{chapterId}, #{relatedCharacters}, #{relatedLocations}, #{relatedWorldSettings}, " +
            "#{conflictPoints}, #{themeTags}, #{createdAt}, #{updatedAt})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(PlotNode plotNode);

    /**
     * 根据ID查找情节节点
     */
    @Select("SELECT * FROM plot_nodes WHERE id = #{id}")
    PlotNode findById(Integer id);

    /**
     * 根据项目ID查找所有情节节点
     */
    @Select("SELECT * FROM plot_nodes WHERE project_id = #{projectId} ORDER BY importance, plot_type, title")
    List<PlotNode> findByProjectId(Integer projectId);

    /**
     * 根据项目ID和重要程度查找情节节点
     */
    @Select("SELECT * FROM plot_nodes WHERE project_id = #{projectId} AND importance = #{importance} ORDER BY plot_type, title")
    List<PlotNode> findByProjectIdAndImportance(@Param("projectId") Integer projectId,
                                                @Param("importance") String importance);

    /**
     * 根据项目ID和情节类型查找情节节点
     */
    @Select("SELECT * FROM plot_nodes WHERE project_id = #{projectId} AND plot_type = #{plotType} ORDER BY title")
    List<PlotNode> findByProjectIdAndType(@Param("projectId") Integer projectId,
                                         @Param("plotType") String plotType);

    /**
     * 根据章节ID查找情节节点
     */
    @Select("SELECT * FROM plot_nodes WHERE chapter_id = #{chapterId} ORDER BY importance, plot_type")
    List<PlotNode> findByChapterId(Integer chapterId);

    /**
     * 查找主线情节
     */
    @Select("SELECT * FROM plot_nodes WHERE project_id = #{projectId} AND importance = 'main' ORDER BY plot_type, title")
    List<PlotNode> findMainPlots(Integer projectId);

    /**
     * 查找高潮情节
     */
    @Select("SELECT * FROM plot_nodes WHERE project_id = #{projectId} AND plot_type = 'climax' ORDER BY title")
    List<PlotNode> findClimaxPlots(Integer projectId);

    /**
     * 根据项目ID和标题查找情节节点
     */
    @Select("SELECT * FROM plot_nodes WHERE project_id = #{projectId} AND title = #{title}")
    PlotNode findByProjectIdAndTitle(@Param("projectId") Integer projectId,
                                     @Param("title") String title);

    /**
     * 更新情节节点
     */
    @Update("UPDATE plot_nodes SET title = #{title}, description = #{description}, " +
            "plot_type = #{plotType}, importance = #{importance}, chapter_id = #{chapterId}, " +
            "related_characters = #{relatedCharacters}, related_locations = #{relatedLocations}, " +
            "related_world_settings = #{relatedWorldSettings}, conflict_points = #{conflictPoints}, " +
            "theme_tags = #{themeTags}, updated_at = #{updatedAt} WHERE id = #{id}")
    int update(PlotNode plotNode);

    /**
     * 删除情节节点
     */
    @Delete("DELETE FROM plot_nodes WHERE id = #{id}")
    int delete(Integer id);

    /**
     * 统计项目的情节节点数量
     */
    @Select("SELECT COUNT(*) FROM plot_nodes WHERE project_id = #{projectId}")
    int countByProjectId(Integer projectId);

    /**
     * 根据重要程度统计项目情节节点数量
     */
    @Select("SELECT COUNT(*) FROM plot_nodes WHERE project_id = #{projectId} AND importance = #{importance}")
    int countByProjectIdAndImportance(@Param("projectId") Integer projectId,
                                      @Param("importance") String importance);

    /**
     * 检查情节节点标题在项目中是否已存在
     */
    @Select("SELECT COUNT(*) FROM plot_nodes WHERE project_id = #{projectId} AND title = #{title} AND id != #{id}")
    int countByTitleExcludingId(@Param("projectId") Integer projectId,
                                @Param("title") String title,
                                @Param("id") Integer id);

    /**
     * 根据情节类型查找所有情节节点（跨项目）
     */
    @Select("SELECT * FROM plot_nodes WHERE plot_type = #{plotType} ORDER BY project_id, title")
    List<PlotNode> findAllByType(String plotType);
}