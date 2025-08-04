package xiaozhi.modules.ragflow.service;

import xiaozhi.modules.ragflow.dto.DatasetDTO;
import java.util.List;

public interface RagflowService {
    List<DatasetDTO> getDatasets(int page, int pageSize);
}