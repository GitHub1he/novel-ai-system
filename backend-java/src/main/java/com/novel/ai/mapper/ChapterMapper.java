package com.novel.ai.mapper;

import com.novel.ai.model.entity.Chapter;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface ChapterMapper {

    @Insert("INSERT INTO chapters (project_id, chapter_number, title, volume, content, outline, summary, " +
            "display_summary, pov_character_id, featured_characters, locations, status, word_count, version, " +
            "created_at, updated_at) " +
            "VALUES (#{projectId}, #{chapterNumber}, #{title}, #{volume}, #{content}, #{outline}, #{summary}, " +
            "#{displaySummary}, #{povCharacterId}, #{featuredCharacters}, #{locations}, #{status}, #{wordCount}, " +
            "#{version}, #{createdAt}, #{updatedAt})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(Chapter chapter);

    @Select("SELECT * FROM chapters WHERE id = #{id}")
    Chapter findById(Integer id);

    @Select("SELECT * FROM chapters WHERE project_id = #{projectId} ORDER BY chapter_number ASC")
    List<Chapter> findByProjectId(Integer projectId);

    @Select("SELECT * FROM chapters WHERE project_id = #{projectId} AND status = #{status} ORDER BY chapter_number ASC")
    List<Chapter> findByProjectIdAndStatus(@Param("projectId") Integer projectId, @Param("status") String status);

    @Select("SELECT * FROM chapters WHERE project_id = #{projectId} ORDER BY created_at DESC LIMIT #{limit} OFFSET #{offset}")
    List<Chapter> findByProjectIdPaginated(@Param("projectId") Integer projectId,
                                          @Param("limit") int limit,
                                          @Param("offset") int offset);

    @Select("SELECT COUNT(*) FROM chapters WHERE project_id = #{projectId}")
    int countByProjectId(Integer projectId);

    @Update("UPDATE chapters SET title = #{title}, content = #{content}, outline = #{outline}, " +
            "summary = #{summary}, display_summary = #{displaySummary}, volume = #{volume}, " +
            "pov_character_id = #{povCharacterId}, featured_characters = #{featuredCharacters}, " +
            "locations = #{locations}, status = #{status}, word_count = #{wordCount}, " +
            "version = #{version}, updated_at = #{updatedAt} WHERE id = #{id}")
    int update(Chapter chapter);

    @Update("UPDATE chapters SET status = #{status}, updated_at = #{updatedAt} WHERE id = #{id}")
    int updateStatus(Chapter chapter);

    @Update("UPDATE chapters SET content = #{content}, word_count = #{wordCount}, version = #{version}, " +
            "updated_at = #{updatedAt} WHERE id = #{id}")
    int updateContent(Chapter chapter);

    @Delete("DELETE FROM chapters WHERE id = #{id}")
    int delete(Integer id);

    @Select("SELECT COUNT(*) FROM chapters WHERE project_id = #{projectId} AND chapter_number = #{chapterNumber}")
    int countByProjectIdAndChapterNumber(@Param("projectId") Integer projectId,
                                        @Param("chapterNumber") Integer chapterNumber);

    @Select("SELECT MAX(chapter_number) FROM chapters WHERE project_id = #{projectId}")
    Integer findMaxChapterNumberByProjectId(Integer projectId);
}