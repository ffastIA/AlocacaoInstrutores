# Frontend — AlocacaoInstrutores

Interface React do simulador de abertura de turmas.

## Requisitos

- Node.js 20 ou superior

## Instalação

```bash
npm install
```

Copie `.env.example` para `.env.local` e ajuste a URL da API se necessário:

```bash
cp .env.example .env.local
```

## Execução

```bash
npm run dev
```

A aplicação sobe em `http://localhost:5173`. Requer o backend rodando (ver `backend/README.md`).

## Build

```bash
npm run build
```

## Lint

```bash
npm run lint
```

## Estrutura

```
src/
  api/         Cliente HTTP, tipos dos contratos, tratamento de erros
  components/  Componentes base do design system
  hooks/       Hooks reutilizáveis (ex.: acompanhamento de operações assíncronas)
  pages/       Telas, divididas em dados/ e simulacao/
  styles/      Tokens visuais e tema
```
