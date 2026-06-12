import { useCallback, useRef } from 'react'
import type { editor } from 'monaco-editor'
import Editor, { type BeforeMount, type OnMount } from '@monaco-editor/react'

const SIMPLES_KEYWORDS = [
  "programa", "inicio", "fim",
  "se", "entao", "senao", "fimse",
  "enquanto", "faca", "fimenquanto",
  "para", "de", "ate", "passo", "fimpara",
  "leia", "escreva", "escreval",
  "procedimento", "retorna",
  "e", "ou", "nao",
  "div", "valor",
] as const

const SIMPLES_TYPES = [
  "inteiro", "flutuante", "vazio", "string",
] as const

const SIMPLES_OPERATORS = ["<-", "+", "-", "*", ">", "<", "=", "<>", ">=", "<="]

const DEFAULT_CODE = `programa exemplo
  inteiro x;

inicio
  escreva "Digite um numero: ";
  leia x;
  escreval "Voce digitou: ", x;
fim`

function registerSimplesLanguage(monaco: Parameters<BeforeMount>[0]) {
  monaco.languages.register({ id: 'simples' })

  monaco.languages.setMonarchTokensProvider('simples', {
    ignoreCase: true,
    keywords: SIMPLES_KEYWORDS,
    types: SIMPLES_TYPES,
    operators: SIMPLES_OPERATORS,
    symbols: /[=<>+\-*]+/,
    tokenizer: {
      root: [
        [/\/\/.*$/, 'comment'],
        [/\/\*/, 'comment', '@block_comment'],
        [/[a-zA-Z_]\w*/, {
          cases: {
            '@types': 'type',
            '@keywords': 'keyword',
            '@default': 'identifier',
          }
        }],
        [/\d+\.\d+/, 'number.float'],
        [/\d+/, 'number'],
        [/<-/, 'operator'],
        [/@symbols/, { cases: { '@operators': 'operator', '@default': '' } }],
        [/[(),;\[\]]/, 'delimiter'],
        [/"[^"]*"/, 'string'],
        [/\s+/, 'white'],
      ],
      block_comment: [
        [/[^/*]+/, 'comment'],
        [/\*\//, 'comment', '@pop'],
        [/[/*]/, 'comment'],
      ],
    },
  })

  monaco.editor.defineTheme('simples-galaxy', {
    base: 'vs-dark',
    inherit: true,
    rules: [
      { token: 'keyword', foreground: '7c3aed', fontStyle: 'bold' },
      { token: 'number', foreground: 'fbbf24' },
      { token: 'number.float', foreground: 'fbbf24' },
      { token: 'string', foreground: '67e8f9' },
      { token: 'delimiter', foreground: 'e2e8f0' },
      { token: 'operator', foreground: 'a78bfa' },
      { token: 'identifier', foreground: 'f1f5f9' },
      { token: 'comment', foreground: '64748b', fontStyle: 'italic' },
      { token: 'type', foreground: 'c4b5fd' },
    ],
    colors: {
      'editor.background': '#020015',
      'editor.foreground': '#f1f5f9',
      'editor.lineHighlightBackground': '#0f0a2e',
      'editor.selectionBackground': '#3b2678',
      'editorCursor.foreground': '#7c3aed',
      'editorCursorWidth': '2',
      'editorLineNumber.foreground': '#1a1145',
      'editorLineNumber.activeForeground': '#7c3aed',
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
