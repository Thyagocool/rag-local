#  Explicação para leigos: o que esse projeto faz?

> Se você não é programador, não se preocupe — vou explicar tudo em português claro, sem termos técnicos.

---

##  O problema que a gente quer resolver

Imagine que você tem **vários documentos** (PDFs, textos, manuais) e quer fazer perguntas sobre eles. Tipo:

- Você tem o manual de 500 páginas de uma máquina
- Quer perguntar: *"Qual a temperatura máxima de operação?"*
- Em vez de procurar manualmente, o **sistema lê tudo e responde pra você**

Parece mágica, mas não é — é o que esse projeto faz.

---

##  Dia 1 — O RAG (o cérebro do projeto)

**RAG** é um nome chique pra um sistema que funciona em 3 passos:

```
 Documento →  Busca →  Resposta
```

### Funciona assim:

**Passo 1 — Alimentar o cérebro**
Você manda um PDF ou texto pro sistema. Ele "lê" e guarda num **banco de memória especial** (chamado banco vetorial).

**Passo 2 — Perguntar**
Você faz uma pergunta. O sistema:
1. Pesquisa na memória dele os trechos mais relevantes
2. Junta com a sua pergunta
3. Manda tudo pro **Ollama** (um "robozinho" inteligente que roda no seu computador)

**Passo 3 — Responder**
O robozinho lê os trechos + sua pergunta e dá uma resposta educada, citando as fontes.

### Exemplo real:

```
Você: "O que diz o documento sobre temperatura?"
Sistema: "O documento informa que a temperatura máxima é 85°C (fonte: manual.pdf, página 23)"
```

### Por que é especial?
-  100% gratuito (usa o Ollama, que roda no seu PC)
-  Funciona offline
-  Não envia seus dados pra ninguém

---

##  Dia 2 — Streaming no RAG (responder conforme pensa)

No Dia 1, quando você perguntava algo, o sistema pensava **a resposta inteira** e só depois te entregava. Assim:

```
Você pergunta →  (pensando...) → "A temperatura máxima é 85°C"
```

No Dia 2, a gente mudou pra ele responder **enquanto pensa**. Agora é assim:

```
Você pergunta →  "A" →  "temperatura" →  "máxima" →  "é" →  "85°C"
```

É como a diferença entre:
-  **Antes**: esperar o amigo terminar de ler o livro pra te contar o final
-  **Agora**: o amigo vai lendo em voz alta e você ouve cada palavra conforme ele lê

### Por que isso é bom?
- **Parece mais rápido** — você vê as palavras chegando
- **Experiência profissional** — igual ChatGPT, Google Bard, etc.
- Dá pra **parar no meio** se a resposta já não tiver fazendo sentido

---

##  Dia 3 — Streaming no Agente (o funcionario esperto)

No Dia 1 e 2, o sistema só respondia perguntas com base nos documentos que você subiu. Ele é tipo um **atendente de livraria** que só sabe dos livros que tem na loja.

No Dia 3, a gente criou um **AGENTE** — um funcionário muito mais esperto que pode:

### O que o agente faz?

Além de consultar os documentos (RAG), ele também pode:

| Ferramenta | O que faz | Exemplo |
|------------|-----------|---------|
|  **Pesquisar docs** | Busca nos seus documentos | "O que diz sobre temperatura?" |
|  **Ver horas** | Diz a data e hora | "Que horas são?" |
|  **Calcular** | Faz contas | "Quanto é 35 + 12?" |
|  **Auto-ajuda** | Explica o que ele sabe fazer | "O que você pode fazer?" |

### O streaming no agente

Igual no Dia 2, o agente também responde **enquanto pensa**, mas com um extra: você vê **quando ele usa as ferramentas**.

```
Você: "Quanto é 150°F em °C?"

 "Vou" →  "precisar" →  "calcular" → 
 [AGENTE USOU A CALCULADORA] → 
 "150" →  "graus" →  "Fahrenheit" → 
 "equivalem" →  "a" →  "65.5" →  "°C"
```

É como assistir um estagiário trabalhando: você vê ele pesquisar no livro, pegar a calculadora, fazer a conta e te dar a resposta — tudo em tempo real.

---

##  Dia 4 — O cerebro que entende livros completos

Antes, quando voce subia um documento, ele era guardado **inteiro**. Mas se o documento tivesse 100 paginas, o sistema nao conseguia encontrar a informacao com precisao.

Agora, o sistema **picota o documento em pedacos menores** (chunks) de forma inteligente:

### Estrategias de chunking

| Estrategia | Funciona assim |
|------------|----------------|
| **Recursiva** | Quebra por paragrafos, frases e palavras — funciona pra qualquer texto |
| **Markdown** | Respeita os titulos (##, ###) do documento — ideal pra arquivos .md |
| **Codigo** | Quebra respeitando funcoes e classes — pra arquivos .py, .js, etc. |
| **Semantica** | (em breve) Vai juntar frases que falam do mesmo assunto |

### Mais formatos

Antes so aceitava PDF, TXT, MD e DOCX. Agora aceita **15 formatos**:

```
PDF, TXT, MD, DOCX, HTML, CSV, JSON,
Python, JavaScript, TypeScript, SQL,
YAML, XML, HTM
```

---

##  Dia 5 — O revisor que melhora as respostas

Quando voce pergunta algo, o sistema busca os pedacos mais relevantes. Mas as vezes um pedaco usa as mesmas palavras mas nao responde a sua pergunta.

O **reranking** resolve isso:

```
SEM RERANKING:
   Busca -> [doc A, doc B, doc C, doc D]
           Resposta pode usar doc irrelevante

COM RERANKING:
   Busca -> [doc A, doc B, ..., doc J]  (busca 10)
        -> Re-ordenados por relevancia
        -> [doc G, doc A, doc D, doc F]  (os 4 melhores)
        -> Resposta mais precisa!
```

E como ter um **revisor** que le os 10 pedacos encontrados e seleciona so os 4 que realmente respondem a sua pergunta.

---

##  Dia 6 — O agente que pesquisa na internet

Antes, o agente so sabia o que estava nos seus documentos. Tipo um funcionario que so conhece os livros da estante.

Agora ele tambem pode **pesquisar na internet**! Ele usa o DuckDuckGo (igual voce usar o Google) pra buscar noticias, previsao do tempo, cotacoes, etc.

### Exemplo:

```
Voce: "Qual a previsao do tempo hoje?"

Agente:
  1. Pesquisa na internet -> "previsao do tempo hoje"
  2. Le os resultados
  3. Responde: "A previsao e de 28 C com pancadas de chuva a tarde"

Voce: "O que diz o manual sobre temperatura maxima?"

Agente:
  1. Busca nos seus documentos -> acha o trecho do manual
  2. Responde: "O manual informa que a temperatura maxima e 85 C"
```

O melhor: ele decide **sozinho** se precisa usar a internet ou consultar seus documentos!

---

##  Resumo visual

```
 ADICIONA DOCUMENTOS
        ↓
┌─────────────────────────────┐
│      BANCO DE MEMORIA       │  <- ChromaDB (arquivo no PC)
│   (onde os docs ficam)      │
└──────────┬──────────────────┘
           ↓
PERGUNTA -> +---------------------+ -> RESPOSTA
           |  RAG (Dia 1)        |
           |  Busca nos docs     |  Resposta completa
           |  Pergunta ao robo   |
           +----------+----------+
                      ↓
           +---------------------+ -> Palavra por palavra
           |  STREAMING (Dia 2)  |    (como digitacao)
           |  Responde em tempo  |
           |  real, palavra por  |
           |  palavra            |
           +----------+----------+
                      ↓
           +---------------------+ -> Palavras + ferramentas
           |  AGENTE (Dia 3)     |    em tempo real
           |  Usa ferramentas    |
           |  Calcula, busca,    |
           |  responde           |
           +----------+----------+
                      ↓
           +---------------------+
           |  CHUNKING (Dia 4)   |  Documentos picados
           |  Divide em pedacos  |  em pedacos inteligentes
           |  15 formatos        |
           +----------+----------+
                      ↓
           +---------------------+
           |  RERANKING (Dia 5)  |  Busca mais, filtra
           |  Re-ordena docs     |  os melhores
           |  Mais relevancia    |
           +----------+----------+
                      ↓
           +---------------------+
           |  WEB SEARCH (Dia 6) |  Agente pesquisa
           |  Internet real      |  na internet
           |  DuckDuckGo gratis  |
           +---------------------+
```

---

##  Como usar na prática

### Mandar documento
```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@manual.pdf"
```
Manda o arquivo pro sistema ler. Aceita PDF, TXT, MD, DOCX, HTML, CSV,
JSON, Python, JavaScript, TypeScript, SQL, YAML, XML.

### Perguntar normal
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "O que diz o documento?"}'
```
Pergunta e espera a resposta completa.

### Perguntar com streaming (mais legal)
```bash
curl -N -X POST http://localhost:8000/api/v1/ask/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "O que diz o documento?"}'
```
Pergunta e vê a resposta chegando palavra por palavra.

### Conversar com o agente inteligente
```bash
curl -N -X POST http://localhost:8000/api/v1/agent/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Resuma os documentos e me diga que horas são"}'
```
Conversa com o agente, que usa ferramentas e responde em tempo real.

---

##  Pra que serve esse projeto?

- **Estudo** — aprender como sistemas de IA funcionam na prática
- **Portfólio** — mostrar em entrevistas que você sabe fazer isso
- **Uso real** — criar um sistema de perguntas e respostas pros seus documentos
- **Base pra mais** — a partir daqui dá pra adicionar frontend, deploy, etc.

>  Tudo 100% gratuito, local e sem depender de serviços pagos!
