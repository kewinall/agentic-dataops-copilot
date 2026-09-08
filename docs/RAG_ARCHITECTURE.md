# RAG Architecture / RAG 架構

## Goal / 目標

v0.3 將原本 hard-coded runbook search 升級成可維護、可評估、可追蹤來源的 Hybrid RAG Knowledge Layer。

## Pipeline

```text
Markdown Documents
       |
       v
Document Loader
       |
       v
Markdown Chunker
       |
       v
KnowledgeChunk
   /          \
Lexical     Hashing Embedder
   |             |
   |         VectorStore
   |             |
   +------+------+
          |
          v
   Hybrid Retriever
          |
          v
      SearchHit
          |
          v
       Citation
          |
     +----+----+
     |         |
 Knowledge   Agent/LLM
    API       Tool Result
```

## Retrieval

目前 scoring 為 65% lexical + 35% vector。Lexical 使用 token overlap + IDF；vector 使用 deterministic feature hashing cosine similarity。

Tokenizer 同時保留英文 technical tokens 與 CJK bigrams，因此適合中英文混合的 DataOps query。

## Why deterministic embedding?

- 不需要網路或 API key。
- GitHub Actions 可重現。
- 適合封閉網段與離線 PoC。
- 可以先穩定 VectorStore、citation 與 evaluation contract。

Production 可再替換成 enterprise embedding model，而不必改 Agent/API contract。

## VectorStore abstraction

v0.3 使用 `VectorStore` protocol + `InMemoryVectorStore`。後續可新增 pgvector、OpenSearch、Qdrant、Milvus 或 Azure AI Search adapter。

## Citation

每筆 citation 包含：`citation_id`、`document_id`、`chunk_id`、`title`、`source`、`score`、`lexical_score`、`vector_score`、`excerpt`。

## Evaluation

Regression dataset 位於 `knowledge/eval/retrieval_cases.jsonl`。

CI 執行：

```bash
python -m agentic_dataops_copilot.knowledge.evaluation --top-k 3 --min-hit-rate 0.90
```

v0.3 release baseline：11 cases、Hit Rate@3 = 1.0、MRR = 1.0。

## Safety

目前流程是 Retrieve → Cite → Analyze → Recommend，不是自動修改 production。RAG evidence 不會繞過既有 deterministic guardrails。
