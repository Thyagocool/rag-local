import { useState, useCallback } from "react";
import Header from "./components/Header";
import Chat from "./components/Chat";
import "./App.css";

function genId(): string {
  return Math.random().toString(36).substring(2, 10);
}

export default function App() {
  const [mode, setMode] = useState<"rag" | "agent">("agent");
  const [threadId, setThreadId] = useState(genId());
  const [notification, setNotification] = useState<string | null>(null);
  const [notifType, setNotifType] = useState<"ok" | "err">("ok");

  const showNotif = useCallback((msg: string, type: "ok" | "err" = "ok") => {
    setNotification(msg);
    setNotifType(type);
    setTimeout(() => setNotification(null), 4000);
  }, []);

  function handleUploadDone(msg: string) {
    showNotif(msg, msg.startsWith("Falha") ? "err" : "ok");
  }

  function handleClearDone() {
    showNotif("Banco vetorial limpo!", "ok");
  }

  function handleNewThread() {
    setThreadId(genId());
  }

  console.log("Notification:", notification)

  return (
    <div className="app">
      <Header
        mode={mode}
        onModeChange={setMode}
        onUploadDone={handleUploadDone}
        onClearDone={handleClearDone}
        threadId={threadId}
        onNewThread={handleNewThread}
      />

      {notification && (
        <div className={`notification ${notifType}`}>
          {notification}
        </div>
      )}

      <Chat mode={mode} threadId={threadId} />
    </div>
  );
}
