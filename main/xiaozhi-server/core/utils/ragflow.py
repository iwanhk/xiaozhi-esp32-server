import requests
from typing import List


class RAGContextProvider:
    def __init__(self, api: str, token: str, topk: int = 5):
        self.api = api.rstrip("/")
        self.token = token
        self.topk = topk

    def retrieve_knowledge_context(self, question: str, dataset_ids: List[str]) -> List[str]:

        url = self.api + "/api/v1/retrieval"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        payload = {
            "question": question,
            "dataset_ids": dataset_ids
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=2,
                verify=False
            )

            response.raise_for_status()
            result = response.json()

            if result.get("code") != 0:
                print(f"RAG接口返回异常: {result}")
                return None

            chunks = result.get("data", {}).get("chunks", [])
            contents = [chunk.get("content", "") for chunk in chunks if chunk.get("content")]

            # 构建适合大模型的上下文内容（每段前加编号，段间两个换行）
            context_text = "\n\n".join(f"{i+1}. {c.strip()}" for i, c in enumerate(contents[:self.topk]))
            return context_text

        except Exception as e:
            print(f"RAG接口请求异常: {e}")
            return None
    