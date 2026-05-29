package com.novel.ai.mapper;

import com.novel.ai.model.entity.WorldSetting;
import org.apache.ibatis.annotations.*;

import java.util.List;

/**
 * 世界观设定数据库访问接口
 * 使用MyBatis注解实现数据库操作
 */
@Mapper
public interface WorldSettingMapper {

    /**
     * 插入新世界观设定
     */
    @Insert("INSERT INTO world_settings (project_id, name, setting_type, description, attributes, " +
            "related_entities, is_core_rule, image, created_at, updated_at) " +
            "VALUES (#{projectId}, #{name}, #{settingType}, #{description}, #{attributes}, " +
            "#{relatedEntities}, #{isCoreRule}, #{image}, #{createdAt}, #{updatedAt})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(WorldSetting worldSetting);

    /**
     * 根据ID查找世界观设定
     */
    @Select("SELECT * FROM world_settings WHERE id = #{id}")
    WorldSetting findById(Integer id);

    /**
     * 根据项目ID查找所有世界观设定
     */
    @Select("SELECT * FROM world_settings WHERE project_id = #{projectId} ORDER BY setting_type, name")
    List<WorldSetting> findByProjectId(Integer projectId);

    /**
     * 根据项目ID和设定类型查找世界观设定
     */
    @Select("SELECT * FROM world_settings WHERE project_id = #{projectId} AND setting_type = #{settingType} ORDER BY name")
    List<WorldSetting> findByProjectIdAndType(@Param("projectId") Integer projectId,
                                           @Param("settingType") String settingType);

    /**
     * 查找项目的核心规则
     */
    @Select("SELECT * FROM world_settings WHERE project_id = #{projectId} AND is_core_rule = 1 ORDER BY setting_type, name")
    List<WorldSetting> findCoreRules(Integer projectId);

    /**
     * 根据项目ID和名称查找世界观设定
     */
    @Select("SELECT * FROM world_settings WHERE project_id = #{projectId} AND name = #{name}")
    WorldSetting findByProjectIdAndName(@Param("projectId") Integer projectId,
                                       @Param("name") String name);

    /**
     * 更新世界观设定
     */
    @Update("UPDATE world_settings SET name = #{name}, setting_type = #{settingType}, " +
            "description = #{description}, attributes = #{attributes}, related_entities = #{relatedEntities}, " +
            "image = #{image}, updated_at = #{updatedAt} WHERE id = #{id} AND (is_core_rule = 0 OR is_core_rule IS NULL)")
    int update(WorldSetting worldSetting);

    /**
     * 删除世界观设定（核心规则不可删除）
     */
    @Delete("DELETE FROM world_settings WHERE id = #{id} AND (is_core_rule = 0 OR is_core_rule IS NULL)")
    int delete(Integer id);

    /**
     * 统计项目的世界观设定数量
     */
    @Select("SELECT COUNT(*) FROM world_settings WHERE project_id = #{projectId}")
    int countByProjectId(Integer projectId);

    /**
     * 根据设定类型统计项目世界观设定数量
     */
    @Select("SELECT COUNT(*) FROM world_settings WHERE project_id = #{projectId} AND setting_type = #{settingType}")
    int countByProjectIdAndType(@Param("projectId") Integer projectId,
                               @Param("settingType") String settingType);

    /**
     * 检查世界观设定名称在项目中是否已存在
     */
    @Select("SELECT COUNT(*) FROM world_settings WHERE project_id = #{projectId} AND name = #{name} AND id != #{id}")
    int countByNameExcludingId(@Param("projectId") Integer projectId,
                              @Param("name") String name,
                              @Param("id") Integer id);

    /**
     * 根据设定类型查找所有世界观设定（跨项目）
     */
    @Select("SELECT * FROM world_settings WHERE setting_type = #{settingType} ORDER BY project_id, name")
    List<WorldSetting> findAllByType(String settingType);
}