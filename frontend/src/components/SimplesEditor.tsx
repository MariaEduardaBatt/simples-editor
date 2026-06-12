import { useCallback, useRef } from 'react'
import type { editor } from 'monaco-editor'
import Editor, { type BeforeMount, type OnMount } from '@monaco-editor/react'

const SIMPLES_KEYWORDS = [
  "programa", "inicio", "fim",
  "inteiro", "flutuante", "vazio",
  "se", "entao", "senao", "fimse",
  "enquanto", "fimenquanto",
  "para", "de", "ate", "passo", "faca", "fimpara",
  "leia", "escreva", "escreval",
  "e", "ou", "nao",
  "div",
  "procedimento", "retorna",
] as const

const SIMPLES_OPERATORS = ["<-", "+", "-", "*", "div", ">", "<", "=", "<>", ">=", "<="]

const DEFAULT_CODE = `programa exemplo
  inteiro x

inicio
  escreva "Digite um numero: "
  leia x
  escreval "Voce digitou: ", x
fim`

function registerSimplesLanguage(monaco: Parameters<BeforeMount>[0]) {
  monaco.languages.register({ id: 'simples' })

  monaco.languages.setMonarchTokensProvider('simples', {
    ignoreCase: true,
    keywords: SIMPLES_KEYWORDS,
    operators: SIMPLES_OPERATORS,
    symbols: /[=<>+\-*]+/,
    tokenizer: {
      root: [
        [/[a-zA-Z_]\w*/, {
          cases: { '@keywords': 'keyword', '@default': 'identifier' }
        }],
        [/\d+\.\d+/, 'number.float'],
        [/\d+/, 'number'],
        [/<-/, 'operator'],
        [/@symbols/, { cases: { '@operators': 'operator', '@default': '' } }],
        [/[(),;]/, 'delimiter'],
        [/"[^"]*"/, 'string'],
        [/\s+/, 'white'],
      ],
    },
  })

  monaco.editor.defineTheme('simples-galaxy', {
    base: 'vs-dark',
    inherit: true,
    rules: [
      { token: 'keyword', foreground: 'a78bfa', fontStyle: 'bold' },
      { token: 'number', foreground: 'fbbf24' },
      { token: 'number.float', foreground: 'fbbf24' },
      { token: 'string', foreground: '67e8f9' },
      { token: 'delimiter', foreground: 'e2e8f0' },
      { token: 'operator', foreground: 'c4b5fd' },
      { token: 'identifier', foreground: 'f1f5f9' },
      { token: 'comment', foreground: '64748b', fontStyle: 'italic' },
      { token: 'type', foreground: 'ddd6fe' },
    ],
    colors: {
      'editor.background': '#020015',
      'editor.foreground': '#f1f5f9',
      'editor.lineHighlightBackground': '#0f0a2e',
      'editor.selectionBackground': '#3b2678',
      'editorCursor.foreground': '#a78bfa',
      'editorCursorWidth': '2',
      'editorLineNumber.foreground': '#1a1145',
      'editorLineNumber.activeForeground': '#8b5cf6',
      'editor.selectionHighlightBackground': '#281a5c',
      'editorBracketMatch.background': '#281a5c80',
      'editorBracketMatch.border': '#7c3aed80',
      'editorRuler.foreground': '#0f0a2e',
      'editorHoverWidget.background': '#07051a',
      'editorHoverWidget.border': '#1a1145',
    },
  })
}

export function SimplesEditor() {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null)

  const handleBeforeMount: BeforeMount = useCallback((monaco) => {
    registerSimplesLanguage(monaco)
  }, [])

  const handleMount: OnMount = useCallback((editorInstance) => {
    editorRef.current = editorInstance
  }, [])

  return (
    <Editor
      height="100%"
      language="simples"
      theme="simples-galaxy"
      value={DEFAULT_CODE}
      beforeMount={handleBeforeMount}
      onMount={handleMount}
      options={{
        minimap: { enabled: false },
        fontSize: 14,
        fontFamily: "'JetBrains Mono', 'Cascadia Code', 'Fira Code', monospace",
        lineNumbers: 'on',
        scrollBeyondLastLine: false,
        automaticLayout: true,
        tabSize: 2,
        renderWhitespace: 'selection',
        wordWrap: 'on',
        padding: { top: 16, bottom: 16 },
      }}
    />
  )
}
