package xiaozhi.modules.ragflow.controller;

import io.swagger.v3.oas.annotations.Operation;

import org.apache.shiro.authz.annotation.RequiresPermissions;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import xiaozhi.common.utils.Result;
import xiaozhi.modules.ragflow.dto.DatasetDTO;
import xiaozhi.modules.ragflow.service.RagflowService;

import java.util.List;

@RestController
@RequestMapping("/ragflow")
public class DatasetController {

    @Autowired
    private RagflowService ragflowService;

    @GetMapping("/datasets")
    @Operation(summary = "获取知识库列表")
    @RequiresPermissions("sys:role:normal")
    public Result<List<DatasetDTO>> getDataset(
        @RequestParam(defaultValue = "1") int page,
        @RequestParam(defaultValue = "1000") int pageSize) {

        List<DatasetDTO> list = ragflowService.getDatasets(page, pageSize);
        return new Result<List<DatasetDTO>>().ok(list);
    }
}