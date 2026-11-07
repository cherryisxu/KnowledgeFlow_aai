import { useCallback, useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";

type SearchResult = {
  chunk_id: string;
  content: string;
  source: string;
  score: number;
};

type AnswerSource = {
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

  type QueryMode = "retrieve" | "answer";
  const [queryMode, setQueryMode] = useState<QueryMode>("retrieve");

  const [answer, setAnswer] = useState("");
  const [answerSources, setAnswerSources] = useState<AnswerSource[]>([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searched, setSearched] = useState(false);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [documentsLoading, setDocumentsLoading] = useState(false);
  const [documentsError, setDocumentsError] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [uploadError, setUploadError] = useState("");
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [deleteMessage, setDeleteMessage] = useState("");
  const [deleteError, setDeleteError] = useState("");

  const fetchDocuments = useCallback(async () => {
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
  }, []);

  useEffect(() => {
    void fetchDocuments();
  }, [fetchDocuments]);

  async function handleUpload() {
    if (!selectedFile) {
      setUploadError("请先选择一个文件");
      return;
    }

    if (selectedFile.size > 5 * 1024 * 1024) {
      setUploadError("文件大小不能超过 5 MB");
      return;
    }

    setUploading(true);
    setUploadMessage("");
    setUploadError("");
    setDeleteMessage("");
    setDeleteError("");

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch("http://127.0.0.1:8000/documents/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "上传失败");
      }

      setUploadMessage("文档上传成功！");
      setSelectedFile(null);

      // 上传成功后清空文件选择框
      const fileInput = document.getElementById(
        "document-upload",
      ) as HTMLInputElement | null;

      if (fileInput) {
        fileInput.value = "";
      }

      // 自动刷新知识库列表
      await fetchDocuments();
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : "上传失败");
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(documentId: number) {
    const confirmed = window.confirm("确定要删除这份文档吗？删除后无法恢复。");

    if (!confirmed) {
      return;
    }

    setDeleteMessage("");
    setDeleteError("");
    setDeletingId(documentId);
    setDeleteMessage("");
    setDeleteError("");

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/documents/${documentId}`,
        {
          method: "DELETE",
        },
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "删除失败");
      }

      setDeleteMessage("文档删除成功！");
      setTimeout(() => {
        setDeleteMessage("");
      }, 3000);

      // 刷新文档列表
      await fetchDocuments();
    } catch (err) {
      setDeleteError(err instanceof Error ? err.message : "删除失败");
    } finally {
      setDeletingId(null);
    }
  }

  async function handleSearch() {
    const question = query.trim();

    if (!question) {
      return;
    }

    setLoading(true);
    setError("");
    setResults([]);
    setAnswer("");
    setAnswerSources([]);
    setSearched(true);

    try {
      // 根据当前模式选择接口
      const endpoint =
        queryMode === "retrieve"
          ? "http://127.0.0.1:8000/retrieve"
          : "http://127.0.0.1:8000/answer";

      const requestBody =
        queryMode === "retrieve"
          ? {
              query: question,
              top_k: 3,
            }
          : {
              question: question,
              top_k: 3,
            };

      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`请求失败：HTTP ${response.status}`);
      }

      const data = await response.json();

      if (queryMode === "retrieve") {
        // 检索模式：保存原始检索结果
        setResults(data.results || []);
      } else {
        // AI 问答模式：保存生成答案和参考来源
        setAnswer(data.answer || "");
        setAnswerSources(data.sources || []);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "搜索失败");
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

        <div className="mode-switch">
          <button
            className={
              queryMode === "retrieve" ? "mode-button active" : "mode-button"
            }
            onClick={() => setQueryMode("retrieve")}
          >
            检索模式
          </button>

          <button
            className={
              queryMode === "answer" ? "mode-button active" : "mode-button"
            }
            onClick={() => setQueryMode("answer")}
          >
            AI 问答模式
          </button>
        </div>

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

        {/* 检索模式 */}
        {!loading && !error && searched && queryMode === "retrieve" && (
          <>
            {results.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">⌕</div>
                <h2>暂时没有找到匹配内容</h2>
                <p>试试换一种问法，或使用知识库中已有的关键词。</p>
              </div>
            ) : (
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
          </>
        )}

        {/* AI 问答模式 */}
        {!loading && !error && searched && queryMode === "answer" && (
          <>
            {!answer ? (
              <div className="empty-state">
                <div className="empty-icon">⌕</div>
                <h2>暂时没有生成回答</h2>
                <p>试试换一种问法，或检查知识库中是否有相关内容。</p>
              </div>
            ) : (
              <div className="results-list">
                <div className="results-heading">
                  <h2>AI 回答</h2>
                  <span>基于知识库生成</span>
                </div>

                <article className="answer-card">
                  <div className="answer-content">
                    <ReactMarkdown>{answer}</ReactMarkdown>
                  </div>
                </article>

                {answerSources.length > 0 && (
                  <div className="sources-section">
                    <div className="results-heading">
                      <h2>参考来源</h2>
                      <span>{answerSources.length} 条参考内容</span>
                    </div>

                    {answerSources.map((source) => (
                      <article className="result-card" key={source.chunk_id}>
                        <div className="result-meta">
                          <span>{source.source}</span>
                          <span>相关性分数：{source.score.toFixed(3)}</span>
                        </div>

                        <p>{source.content}</p>

                        <span className="chunk-id">ID：{source.chunk_id}</span>
                      </article>
                    ))}
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </section>

      <section className="upload-section">
        <div className="upload-heading">
          <p className="eyebrow">ADD NEW DOCUMENT</p>
          <h2>上传知识文档</h2>
          <p>上传 TXT 或 Markdown 文件，扩展你的知识库。</p>
        </div>

        <div className="upload-card">
          <div className="upload-icon">↑</div>

          <h3>选择一个文件</h3>
          <p>支持 .txt、.md 格式，最大 5 MB</p>

          <input
            id="document-upload"
            type="file"
            accept=".txt,.md,text/plain,text/markdown"
            onChange={(event) => {
              setSelectedFile(event.target.files?.[0] || null);
              setUploadMessage("");
              setUploadError("");
            }}
          />

          {selectedFile && (
            <p className="selected-file">已选择：{selectedFile.name}</p>
          )}

          <button
            className="upload-button"
            onClick={handleUpload}
            disabled={!selectedFile || uploading}
          >
            {uploading ? "正在上传..." : "上传文档"}
          </button>

          {uploadMessage && <p className="upload-success">{uploadMessage}</p>}

          {uploadError && <p className="upload-error">{uploadError}</p>}
        </div>
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

        {deleteMessage && <p className="upload-success">{deleteMessage}</p>}

        {deleteError && <p className="upload-error">{deleteError}</p>}

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

                <div className="document-actions">
                  <span className="document-status">
                    {doc.status === "completed" ? "已完成" : doc.status}
                  </span>

                  <button
                    className="delete-button"
                    onClick={() => handleDelete(doc.id)}
                    disabled={deletingId === doc.id}
                  >
                    {deletingId === doc.id ? "删除中..." : "删除"}
                  </button>
                </div>
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
