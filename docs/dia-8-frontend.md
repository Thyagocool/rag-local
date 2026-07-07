# Dia 8 — Frontend básico (React + Vite + TypeScript)

> **Status: IMPLEMENTADO**  
> Frontend completo e funcional, com build gerado em `dist/`.

---

## Visão geral

Frontend em **React 19 + Vite 8 + TypeScript 6**, criado com `create-vite`.  
Se comunica com o backend via proxy do Vite (`/api` → `localhost:8000`).

---

## Estrutura de arquivos

```
frontend/
├── index.html                          # Entry point HTML
├── package.json                        # React 19, Vitest, Testing Library
├── vite.config.ts                      # Proxy /api + config de teste
├── tsconfig.json / tsconfig.app.json / tsconfig.node.json
├── .oxlintrc.json
├── public/
│   ├── favicon.svg
│   └── icons.svg
├── src/
│   ├── main.tsx                        # Entry React (StrictMode)
│   ├── App.tsx                         # Componente principal (56 linhas)
│   ├── App.css                         # Tema escuro completo
│   ├── App.test.tsx                    # Teste básico (2 asserts)
│   ├── index.css                       # Reset básico
│   ├── assets/
│   │   ├── hero.png
│   │   ├── react.svg
│   │   └── vite.svg
│   ├── components/
│   │   ├── Chat.tsx                    # Componente de chat (254 linhas)
│   │   └── Header.tsx                  # Header com upload, modos, etc (125 linhas)
│   ├── services/
│   │   └── api.ts                      # Camada de API (168 linhas)
│   └── test/
│       └── setup.ts                    # Setup jsdom para testes
└── dist/                               # Build gerado (não versionado)
```

---

## Funcionalidades implementadas

### 1. Dois modos de operação
- **RAG:** perguntas sobre documentos indexados
- **Agent:** conversa com agente (RAG + tools + web search)
- Toggle visual entre os modos no header

### 2. Streaming de respostas (SSE)
- **RAG:** `POST /api/v1/ask/stream` → tokens em tempo real
- **Agent:** `POST /api/v1/agent/stream` → tokens, tool_calls, tool_results
- Fallback automático para requisição completa se streaming falhar

### 3. Upload de documentos
- Botão Upload no header
- Suporte aos mesmos 15 formatos do backend
- Feedback visual com notificação de sucesso/erro

### 4. Limpeza do banco vetorial
- Botão Limpar com confirmação (`confirm()`)
- Notificação de conclusão

### 5. Múltiplas conversas (threads)
- Botão "Novo" gera nova `thread_id`
- Exibição do ID parcial (`#abcd12`) no header (modo agent)
- Chat é resetado ao trocar de modo

### 6. Exibição de fontes
- Respostas RAG mostram número de fontes
- Toggle para expandir/recolher conteúdo das fontes

### 7. Tratamento de dados
- **Dedup:** remove texto duplicado consecutivo (modelo "gaguejando")
- **Strip tool JSON:** remove JSON de tool calls que vazam na resposta
- **Dedup de eventos:** evita tokens duplicados entre eventos SSE

### 8. UI/UX
- Tema escuro
- Scroll automático para novas mensagens
- Indicador "pensando..." durante carregamento
- Atalho Enter para enviar (Shift+Enter para nova linha)
- Design responsivo

---

## Conexão com backend

O `vite.config.ts` configura proxy:

```ts
server: {
  port: 5173,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

O `api.ts` usa `API_BASE = "/api/v1"` — em dev, o proxy do Vite redireciona para o backend.

### Para rodar

```bash
# Terminal 1 — Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

Acessar: `http://localhost:5173`

---

## Build de produção

```bash
cd frontend
npm run build    # gera dist/
```

O build já foi gerado e está em `frontend/dist/`.
