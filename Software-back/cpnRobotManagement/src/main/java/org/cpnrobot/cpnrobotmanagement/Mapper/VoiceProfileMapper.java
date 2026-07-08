package org.cpnrobot.cpnrobotmanagement.Mapper;

import org.apache.ibatis.annotations.Delete;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Options;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;
import pojos.VoiceProfile;

import java.util.List;

@Mapper
public interface VoiceProfileMapper {

    String COLUMNS = """
            id,
            user_id as userId,
            name,
            engine,
            status,
            reference_audio_path as referenceAudioPath,
            reference_text as referenceText,
            model_path as modelPath,
            is_default as defaultProfile,
            last_error as lastError,
            created_at as createdAt,
            updated_at as updatedAt
            """;

    @Select("select " + COLUMNS + " from voice_profile where user_id = #{userId} order by is_default desc, updated_at desc")
    List<VoiceProfile> listByUserId(Integer userId);

    @Select("select " + COLUMNS + " from voice_profile where id = #{id} and user_id = #{userId}")
    VoiceProfile getByIdAndUserId(@Param("id") Long id, @Param("userId") Integer userId);

    @Select("select " + COLUMNS + " from voice_profile where user_id = #{userId} and is_default = true limit 1")
    VoiceProfile getDefaultByUserId(Integer userId);

    @Insert("""
            insert into voice_profile(
              user_id, name, engine, status, reference_audio_path, reference_text,
              model_path, is_default, last_error
            ) values (
              #{userId}, #{name}, #{engine}, #{status}, #{referenceAudioPath}, #{referenceText},
              #{modelPath}, #{defaultProfile}, #{lastError}
            )
            """)
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(VoiceProfile profile);

    @Update("""
            update voice_profile
            set status = #{status},
                model_path = #{modelPath},
                last_error = #{lastError},
                updated_at = current_timestamp
            where id = #{id} and user_id = #{userId}
            """)
    int updateTrainingState(VoiceProfile profile);

    @Update("update voice_profile set is_default = false where user_id = #{userId}")
    int clearDefault(Integer userId);

    @Update("update voice_profile set is_default = true, updated_at = current_timestamp where id = #{id} and user_id = #{userId}")
    int setDefault(@Param("id") Long id, @Param("userId") Integer userId);

    @Delete("delete from voice_profile where id = #{id} and user_id = #{userId}")
    int deleteByIdAndUserId(@Param("id") Long id, @Param("userId") Integer userId);
}
