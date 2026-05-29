package com.novel.ai.mapper;

import com.novel.ai.model.entity.User;
import org.apache.ibatis.annotations.*;

import java.time.LocalDateTime;
import java.util.List;

@Mapper
public interface UserMapper {

    @Insert("INSERT INTO users (email, username, hashed_password, phone, avatar, preferred_genre, is_admin, is_active, created_at, updated_at) " +
            "VALUES (#{email}, #{username}, #{hashedPassword}, #{phone}, #{avatar}, #{preferredGenre}, #{isAdmin}, #{isActive}, #{createdAt}, #{updatedAt})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(User user);

    @Select("SELECT * FROM users WHERE id = #{id}")
    User findById(Integer id);

    @Select("SELECT * FROM users WHERE email = #{email}")
    User findByEmail(String email);

    @Select("SELECT * FROM users WHERE username = #{username}")
    User findByUsername(String username);

    @Select("SELECT * FROM users WHERE is_active = 1")
    List<User> findAllActive();

    @Update("UPDATE users SET email = #{email}, username = #{username}, phone = #{phone}, avatar = #{avatar}, " +
            "preferred_genre = #{preferredGenre}, updated_at = #{updatedAt} WHERE id = #{id}")
    int update(User user);

    @Update("UPDATE users SET hashed_password = #{hashedPassword}, updated_at = #{updatedAt} WHERE id = #{id}")
    int updatePassword(User user);

    @Update("UPDATE users SET is_active = #{isActive}, updated_at = #{updatedAt} WHERE id = #{id}")
    int updateActiveStatus(User user);

    @Delete("DELETE FROM users WHERE id = #{id}")
    int delete(Integer id);

    @Select("SELECT COUNT(*) FROM users WHERE email = #{email}")
    int countByEmail(String email);

    @Select("SELECT COUNT(*) FROM users WHERE username = #{username}")
    int countByUsername(String username);
}