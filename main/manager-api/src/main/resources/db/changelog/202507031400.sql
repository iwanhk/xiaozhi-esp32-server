--
-- 表的结构 `tbl_content`
--

CREATE TABLE `tbl_content` (
  `id` int NOT NULL,
  `code` int DEFAULT NULL COMMENT '编码',
  `category_id` int DEFAULT NULL COMMENT '分类id',
  `img_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '图片地址',
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '名称',
  `introduction` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '简介',
  `content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '内容',
  `voice` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '语音',
  `sort` int DEFAULT '0' COMMENT '分类排序',
  `status` tinyint NOT NULL DEFAULT '0' COMMENT '开启状态',
  `creator` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '创建者',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '更新者',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` bit(1) NOT NULL DEFAULT b'0' COMMENT '是否删除',
  `tenant_id` bigint NOT NULL DEFAULT '0' COMMENT '租户编号'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='内容表' ROW_FORMAT=DYNAMIC;

--
-- 转储表的索引
--

--
-- 表的索引 `tbl_content`
--
ALTER TABLE `tbl_content`
  ADD PRIMARY KEY (`id`) USING BTREE,
  ADD UNIQUE KEY `code` (`code`);

--
-- 在导出的表使用AUTO_INCREMENT
--

--
-- 使用表AUTO_INCREMENT `tbl_content`
--
ALTER TABLE `tbl_content`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;
COMMIT;
