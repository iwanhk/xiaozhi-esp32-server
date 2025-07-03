package xiaozhi.modules.content.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import xiaozhi.common.service.impl.BaseServiceImpl;
import xiaozhi.modules.content.dao.TblContentDao;
import xiaozhi.modules.content.entity.TblContentEntity;
import xiaozhi.modules.content.service.TblContentService;

@Slf4j
@Service
@AllArgsConstructor
public class TblContentServiceImpl extends BaseServiceImpl<TblContentDao, TblContentEntity> implements TblContentService {


    @Override
    public TblContentEntity selectByCode(Integer code) {
        LambdaQueryWrapper<TblContentEntity> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(TblContentEntity::getCode, code);
        return this.baseDao.selectOne(queryWrapper);
    }
}
