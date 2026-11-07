import { useEffect, useState } from "react";
import "./App.css";

type SearchResult = {
  chunk_id: string;
  content: string;
  source: string;
  score: number;
};

type Document = {
  id: number;
  filename: string;
  file_type: string;
  status: string;
  chunk_count: number;
  created_at: string;
  updated_at: string;
};

type DocumentsResponse = {
  count: number;
  documents: Document[];
};

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searched, setSearched] = useState(false);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [documentsLoading, setDocumentsLoading] = useState(false);
  const [documentsError, setDocumentsError] = useState("");

  useEffect(() => {
    void fetchDocuments();
  }, []);

  async function fetchDocuments() {
    setDocumentsLoading(true);
    setDocumentsError("");

    try {
      const response = await fetch("http://127.0.0.1:8000/documents");

      if (!response.ok) {
        throw new Error(`请求失败：HTTP ${response.status}`);
      }

      const data: DocumentsResponse = await response.json();

      setDocuments(data.documents);
    } catch (err) {
      setDocumentsError(err instanceof Error ? err.message : "获取文档失败");
    } finally {
      setDocumentsLoading(false);
    }
  }

  async function handleSearch() {
    const question = query.trim();

    if (!question || loading) return;

    setLoading(true);
    setError("");
    setResults([]);
    setSearched(false);

    try {
      const response = await fetch("http://127.0.0.1:8000/retrieve", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: question,
          top_k: 3,
        }),
      });

      if (!response.ok) {
        throw new Error(`请求失败：HTTP ${response.status}`);
      }

      const data = await response.json();

      setResults(data.results);
      setSearched(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "发生了未知错误");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app">
      <header className="header">
        <a className="logo" href="/">
          <span className="logo-icon">K</span>
          KnowledgeFlow AI
        </a>
        <span className="status">Knowledge Assistant</span>
      </header>

      <section className="hero">
        <p className="eyebrow">YOUR PERSONAL KNOWLEDGE SPACE</p>

        <h1>
          让知识流动起来<span>.</span>
        </h1>

        <p className="subtitle">搜索你的知识库，快速找到真正需要的信息。</p>

        <form
          className="search-box"
          onSubmit={(event) => {
            event.preventDefault();
            void handleSearch();
          }}
        >
          <input
            type="text"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="试试输入：Python 列表如何添加元素？"
            aria-label="输入检索问题"
          />

          <button type="submit" disabled={loading || !query.trim()}>
            {loading ? "搜索中…" : "搜索 ↗"}
          </button>
        </form>

        <p className="hint">从一个问题开始，发现知识之间的联系。</p>
      </section>

      <section className="results-section" aria-live="polite">
        {loading && <p className="feedback">正在搜索你的知识库…</p>}

        {error && (
          <div className="feedback error">
            <h2>搜索失败</h2>
            <p>{error}</p>
            <p>请检查 FastAPI 服务是否正在运行。</p>
          </div>
        )}

        {!loading && !error && !searched && (
          <div className="empty-state">
            <div className="empty-icon">⌕</div>
            <h2>你的知识探索之旅</h2>
            <p>输入一个问题，开始检索。</p>
          </div>
        )}

        {!loading && searched && results.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">⌕</div>
            <h2>暂时没有找到匹配内容</h2>
            <p>试试换一种问法，或使用知识库中已有的关键词。</p>
          </div>
        )}

        {!loading && searched && results.length > 0 && (
          <div className="results-list">
            <div className="results-heading">
              <h2>检索结果</h2>
              <span>找到 {results.length} 条内容</span>
            </div>

            {results.map((result) => (
              <article className="result-card" key={result.chunk_id}>
                <div className="result-meta">
                  <span>{result.source}</span>
                  <span>相关性分数：{result.score.toFixed(3)}</span>
                </div>

                <p>{result.content}</p>

                <span className="chunk-id">ID：{result.chunk_id}</span>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="documents-section">
        <div className="documents-heading">
          <div>
            <p className="eyebrow">YOUR KNOWLEDGE BASE</p>
            <h2>我的知识库</h2>
          </div>

          <span className="document-count">共 {documents.length} 份文档</span>
        </div>

        {documentsLoading && <p className="feedback">正在加载文档...</p>}

        {documentsError && (
          <div className="feedback error">{documentsError}</div>
        )}

        {!documentsLoading && !documentsError && documents.length === 0 && (
          <div className="empty-state">
            <h2>知识库还是空的</h2>
            <p>上传第一份文档，开始构建你的知识库。</p>
          </div>
        )}

        {!documentsLoading && !documentsError && documents.length > 0 && (
          <div className="documents-list">
            {documents.map((doc) => (
              <article className="document-card" key={doc.id}>
                <div className="document-info">
                  <div className="document-icon">
                    {doc.file_type.toUpperCase()}
                  </div>

                  <div>
                    <h3>{doc.filename}</h3>
                    <p>{doc.chunk_count} 个文本片段</p>
                  </div>
                </div>

                <span className="document-status">
                  {doc.status === "completed" ? "已完成" : doc.status}
                </span>
              </article>
            ))}
          </div>
        )}
      </section>

      <footer className="footer">
        <span>KnowledgeFlow AI</span>
        <span>Powered by your knowledge</span>
      </footer>
    </main>
  );
}

export default App;
