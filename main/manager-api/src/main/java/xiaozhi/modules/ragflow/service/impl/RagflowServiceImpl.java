package xiaozhi.modules.ragflow.service.impl;

import com.alibaba.fastjson2.JSON;
import com.alibaba.fastjson2.JSONArray;
import com.alibaba.fastjson2.JSONObject;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import org.apache.commons.lang3.StringUtils;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import xiaozhi.common.constant.Constant;
import xiaozhi.modules.ragflow.dto.DatasetDTO;
import xiaozhi.modules.ragflow.service.RagflowService;
import xiaozhi.modules.sys.service.SysParamsService;

import java.util.ArrayList;
import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class RagflowServiceImpl implements RagflowService {

    private final SysParamsService sysParamsService;
    private final RestTemplate restTemplate = new RestTemplate();

    @Override
    public List<DatasetDTO> getDatasets(int page, int pageSize) {
        String apiUrl = sysParamsService.getValue(Constant.RAGFLOW_API, true);
        if (StringUtils.isBlank(apiUrl) || "null".equals(apiUrl)) {
            log.warn("缺少 RAGFLOW_API 参数，请配置系统参数 ragflow.api");
            return new ArrayList<>();
        }

        String token = sysParamsService.getValue(Constant.RAGFLOW_TOKEN, true);
        if (StringUtils.isBlank(token) || "null".equals(token)) {
            log.warn("缺少 RAGFLOW_TOKEN 参数，请配置系统参数 ragflow.token");
            return new ArrayList<>();
        }

        String urlPath = "/api/v1/datasets";
        String urlWithParams = String.format("%s%s?page=%d&page_size=%d", apiUrl, urlPath, page, pageSize);

        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", "Bearer " + token);
        HttpEntity<Void> entity = new HttpEntity<>(headers);

        ResponseEntity<String> response = restTemplate.exchange(urlWithParams, HttpMethod.GET, entity, String.class);

        if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
            try {
                JSONObject json = JSON.parseObject(response.getBody());
                int code = json.getIntValue("code");
                if (code != 0) {
                    log.warn("Ragflow接口返回错误code: {}", code);
                    return new ArrayList<>();
                }

                JSONArray data = json.getJSONArray("data");
                if (data == null) {
                    log.warn("Ragflow接口返回数据中data为空");
                    return new ArrayList<>();
                }
                return data.toJavaList(DatasetDTO.class);
            } catch (Exception e) {
                log.error("解析ragflow接口返回数据失败", e);
            }
        } else {
            log.warn("调用ragflow接口失败，状态码: {}", response.getStatusCode());
        }

        return new ArrayList<>();
    }
}
