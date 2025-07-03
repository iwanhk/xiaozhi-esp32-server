package xiaozhi.modules.content.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.util.Date;

@Data
@EqualsAndHashCode(callSuper = false)
@TableName("tbl_content")
@Schema(description = "内容信息")
public class TblContentEntity {

    @TableId(type = IdType.ASSIGN_UUID)
    @Schema(description = "ID")
    private String id;

    @Schema(description = "编码")
    private Integer code;

    @Schema(description = "分类ID")
    private Integer categoryId;

    @Schema(description = "图片地址")
    private String imgUrl;

    @Schema(description = "名称")
    private String name;

    @Schema(description = "简介")
    private String introduction;

    @Schema(description = "内容")
    private String content;

    @Schema(description = "语音")
    private String voice;

    @Schema(description = "分类排序")
    private Integer sort = 0;

    @Schema(description = "开启状态（0：关闭，1：开启）")
    private Integer status = 0;

    @Schema(description = "创建者")
    private String creator = "";

    @Schema(description = "创建时间")
    private Date createTime;

    @Schema(description = "更新者")
    private String updater = "";

    @Schema(description = "更新时间")
    private Date updateTime;

    @Schema(description = "是否删除（0：未删除，1：已删除）")
    private Integer deleted;

    @Schema(description = "租户编号")
    private Long tenantId;
}