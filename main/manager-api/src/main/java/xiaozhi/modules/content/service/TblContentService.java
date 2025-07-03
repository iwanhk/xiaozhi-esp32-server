package xiaozhi.modules.content.service;

import xiaozhi.common.service.BaseService;
import xiaozhi.modules.content.entity.TblContentEntity;

public interface TblContentService extends BaseService<TblContentEntity> {

    TblContentEntity selectByCode(Integer code);
}