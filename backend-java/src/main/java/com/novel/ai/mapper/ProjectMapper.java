package com.novel.ai.mapper;

import com.novel.ai.model.entity.Project;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface ProjectMapper {

    @Insert("INSERT INTO projects (user_id, title, author, genre, tags, summary, target_readers, status, default_pov, " +
            "style, style_keywords, language_style, sensory_focus, style_intensity, target_words_per_chapter, " +
            "background_template, total_words, total_chapters, completion_rate, created_at, updated_at) " +
            "VALUES (#{userId}, #{title}, #{author}, #{genre}, #{tags}, #{summary}, #{targetReaders}, #{status}, " +
            "#{defaultPov}, #{style}, #{styleKeywords}, #{languageStyle}, #{sensoryFocus}, #{styleIntensity}, " +
            "#{targetWordsPerChapter}, #{backgroundTemplate}, #{totalWords}, #{totalChapters}, #{completionRate}, " +
            "#{createdAt}, #{updatedAt})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(Project project);

    @Select("SELECT * FROM projects WHERE id = #{id}")
    Project findById(Integer id);

    @Select("SELECT * FROM projects WHERE user_id = #{userId} ORDER BY created_at DESC")
    List<Project> findByUserId(Integer userId);

    @Select("SELECT * FROM projects WHERE user_id = #{userId} AND status = #{status} ORDER BY created_at DESC")
    List<Project> findByUserIdAndStatus(@Param("userId") Integer userId, @Param("status") String status);

    @Select("SELECT * FROM projects ORDER BY created_at DESC LIMIT #{limit} OFFSET #{offset}")
    List<Project> findAll(@Param("limit") int limit, @Param("offset") int offset);

    @Update("UPDATE projects SET title = #{title}, author = #{author}, genre = #{genre}, tags = #{tags}, " +
            "summary = #{summary}, target_readers = #{targetReaders}, status = #{status}, default_pov = #{defaultPov}, " +
            "style = #{style}, style_keywords = #{styleKeywords}, language_style = #{languageStyle}, " +
            "sensory_focus = #{sensoryFocus}, style_intensity = #{styleIntensity}, " +
            "target_words_per_chapter = #{targetWordsPerChapter}, background_template = #{backgroundTemplate}, " +
            "updated_at = #{updatedAt} WHERE id = #{id}")
    int update(Project project);

    @Update("UPDATE projects SET total_words = #{totalWords}, total_chapters = #{totalChapters}, " +
            "completion_rate = #{completionRate}, updated_at = #{updatedAt} WHERE id = #{id}")
    int updateStatistics(Project project);

    @Delete("DELETE FROM projects WHERE id = #{id}")
    int delete(Integer id);

    @Select("SELECT COUNT(*) FROM projects WHERE user_id = #{userId}")
    int countByUserId(Integer userId);

    @Select("SELECT COUNT(*) FROM projects WHERE user_id = #{userId} AND status = #{status}")
    int countByUserIdAndStatus(@Param("userId") Integer userId, @Param("status") String status);
}