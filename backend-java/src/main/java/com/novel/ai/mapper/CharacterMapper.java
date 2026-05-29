package com.novel.ai.mapper;

import com.novel.ai.model.entity.Character;
import org.apache.ibatis.annotations.*;

import java.util.List;

/**
 * 人物数据库访问接口
 * 使用MyBatis注解实现数据库操作
 */
@Mapper
public interface CharacterMapper {

    /**
     * 插入新人物
     */
    @Insert("INSERT INTO characters (project_id, name, age, gender, appearance, identity, hometown, " +
            "role, personality, core_motivation, fears, desires, character_arcs, voice_styles, " +
            "created_at, updated_at) " +
            "VALUES (#{projectId}, #{name}, #{age}, #{gender}, #{appearance}, #{identity}, #{hometown}, " +
            "#{role}, #{personality}, #{coreMotivation}, #{fears}, #{desires}, #{characterArcs}, #{voiceStyles}, " +
            "#{createdAt}, #{updatedAt})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(Character character);

    /**
     * 根据ID查找人物
     */
    @Select("SELECT * FROM characters WHERE id = #{id}")
    Character findById(Integer id);

    /**
     * 根据项目ID查找所有人物
     */
    @Select("SELECT * FROM characters WHERE project_id = #{projectId} ORDER BY name ASC")
    List<Character> findByProjectId(Integer projectId);

    /**
     * 根据项目ID和角色类型查找人物
     */
    @Select("SELECT * FROM characters WHERE project_id = #{projectId} AND role = #{role} ORDER BY name ASC")
    List<Character> findByProjectIdAndRole(@Param("projectId") Integer projectId,
                                          @Param("role") String role);

    /**
     * 根据项目ID和名称查找人物
     */
    @Select("SELECT * FROM characters WHERE project_id = #{projectId} AND name = #{name}")
    Character findByProjectIdAndName(@Param("projectId") Integer projectId,
                                     @Param("name") String name);

    /**
     * 查找主角（protagonist）
     */
    @Select("SELECT * FROM characters WHERE project_id = #{projectId} AND role = 'protagonist' ORDER BY name ASC")
    List<Character> findProtagonists(Integer projectId);

    /**
     * 查找反派（antagonist）
     */
    @Select("SELECT * FROM characters WHERE project_id = #{projectId} AND role = 'antagonist' ORDER BY name ASC")
    List<Character> findAntagonists(Integer projectId);

    /**
     * 更新人物信息
     */
    @Update("UPDATE characters SET name = #{name}, age = #{age}, gender = #{gender}, " +
            "appearance = #{appearance}, identity = #{identity}, hometown = #{hometown}, " +
            "role = #{role}, personality = #{personality}, core_motivation = #{coreMotivation}, " +
            "fears = #{fears}, desires = #{desires}, character_arcs = #{characterArcs}, " +
            "voice_styles = #{voiceStyles}, updated_at = #{updatedAt} WHERE id = #{id}")
    int update(Character character);

    /**
     * 删除人物
     */
    @Delete("DELETE FROM characters WHERE id = #{id}")
    int delete(Integer id);

    /**
     * 统计项目的人物数量
     */
    @Select("SELECT COUNT(*) FROM characters WHERE project_id = #{projectId}")
    int countByProjectId(Integer projectId);

    /**
     * 根据角色类型统计项目人物数量
     */
    @Select("SELECT COUNT(*) FROM characters WHERE project_id = #{projectId} AND role = #{role}")
    int countByProjectIdAndRole(@Param("projectId") Integer projectId,
                                @Param("role") String role);

    /**
     * 检查人物名称在项目中是否已存在
     */
    @Select("SELECT COUNT(*) FROM characters WHERE project_id = #{projectId} AND name = #{name} AND id != #{id}")
    int countByNameExcludingId(@Param("projectId") Integer projectId,
                               @Param("name") String name,
                               @Param("id") Integer id);
}