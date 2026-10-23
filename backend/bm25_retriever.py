
import jieba
from rank_bm25 import BM25Okapi


class BM25Retriever:
    def __init__(self, chunks: list[dict]):
        """
        初始化检索器。
        chunks 是知识库中的文本片段列表。
        """
        self.chunks = chunks

        # 1. 对每个片段分词
        self.tokenized_chunks = [
            self._tokenize(chunk["content"])
            for chunk in chunks
        ]

        # 2. 初始化 BM25 算法
        # 空语料不建立 BM25 实例
        if self.tokenized_chunks and all(self.tokenized_chunks):
            self.bm25 = BM25Okapi(self.tokenized_chunks)
        else:
            self.bm25 = None

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """将文本切分成词语。"""
        return [
            word.strip().lower()
            for word in jieba.lcut(text)
            if word.strip()
        ]

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[dict]:
        """
        根据问题检索相关片段。
        返回分数最高的 top_k 个结果。
        """
        if not query.strip() or top_k <= 0:
            return []

        if self.bm25 is None:
            return []

        # 3. 对用户问题分词
        query_tokens = self._tokenize(query)

        if not query_tokens:
            return []

        # 4. 计算每个片段的 BM25 分数
        scores = self.bm25.get_scores(query_tokens)

        # 5. 按分数从高到低排序
        ranked_indices = sorted(
            range(len(self.chunks)),
            key=lambda index: scores[index],
            reverse=True,
        )

        # 6. 返回 Top-K 结果
        results = []

        for index in ranked_indices:
            score = float(scores[index])

            # 没有匹配到有效分数时，不返回该片段
            if score <= 0:
                continue

            chunk = self.chunks[index]

            results.append({
                "chunk_id": chunk["chunk_id"],
                "content": chunk["content"],
                "source": chunk["source"],
                "score": score,
            })

            if len(results) >= top_k:
                break

        return results
