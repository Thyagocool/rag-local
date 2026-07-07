import { useState, useRef } from "react";
import { uploadDocument, clearDocuments } from "../services/api";

interface HeaderProps {
  mode: "rag" | "agent";
  onModeChange: (mode: "rag" | "agent") => void;
  onUploadDone: (msg: string) => void;
  onClearDone: () => void;
  threadId: string;
  onNewThread: () => void;
}

export default function Header({
  mode,
  onModeChange,
  onUploadDone,
  onClearDone,
  threadId,
  onNewThread,
}: HeaderProps) {
  const [uploading, setUploading] = useState(false);
  const [clearing, setClearing] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  async function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const res = await uploadDocument(file);
      onUploadDone(
        `${file.name} indexado (${res.documents_processed} chunks)`,
      );
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Erro no upload";
      onUploadDone(`Falha: ${msg}`);
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  async function handleClear() {
    if (!confirm("Limpar todos os documentos do banco?")) return;

    setClearing(true);
    try {
      await clearDocuments();
      onClearDone();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Erro ao limpar";
      alert(msg);
    } finally {
      setClearing(false);
    }
  }

  return (
    <header className="header">
      <div className="header-left">
        <h1 className="header-title">RAG Chat</h1>
        <span className="header-subtitle">Local IA</span>
      </div>

      <div className="header-center">
        <div className="mode-toggle">
          <button
            className={`mode-btn ${mode === "rag" ? "active" : ""}`}
            onClick={() => onModeChange("rag")}
          >
            RAG
          </button>
          <button
            className={`mode-btn ${mode === "agent" ? "active" : ""}`}
            onClick={() => onModeChange("agent")}
          >
            Agent
          </button>
        </div>
      </div>

      <div className="header-right">
        <input
          ref={fileRef}
          type="file"
          accept=".pdf,.txt,.md,.docx,.html,.csv,.json,.py,.js,.ts,.sql"
          hidden
          onChange={handleFile}
        />
        <button
          className="btn btn-upload"
          disabled={uploading}
          onClick={() => fileRef.current?.click()}
          title="Upload de documento"
        >
          {uploading ? "Enviando..." : "Upload"}
        </button>

        <button
          className="btn btn-clear"
          disabled={clearing}
          onClick={handleClear}
          title="Limpar banco"
        >
          {clearing ? "Limpando..." : "Limpar"}
        </button>

        <button
          className="btn btn-new"
          onClick={onNewThread}
          title="Nova conversa"
        >
          Novo
        </button>

        {mode === "agent" && (
          <span className="thread-id" title="ID da conversa">
            #{threadId.slice(0, 6)}
          </span>
        )}
      </div>
    </header>
  );
}
