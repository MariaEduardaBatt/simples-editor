import { useCallback, useEffect, useRef } from 'react'
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
      { token: 'keyword', foreground: '5E00A0', fontStyle: 'bold' },
      { token: 'number', foreground: 'fbbf24' },
      { token: 'number.float', foreground: 'fbbf24' },
      { token: 'string', foreground: '67e8f9' },
      { token: 'delimiter', foreground: 'e2e8f0' },
      { token: 'operator', foreground: '5E00A0' },
      { token: 'identifier', foreground: 'f1f5f9' },
      { token: 'comment', foreground: '4a5568', fontStyle: 'italic' },
      { token: 'type', foreground: 'ddd6fe' },
    ],
    colors: {
      'editor.background': '#000008',
      'editor.foreground': '#f1f5f9',
      'editor.lineHighlightBackground': '#0a0418',
      'editor.selectionBackground': '#5E00A0',
      'editorCursor.foreground': '#5E00A0',
      'editorCursorWidth': '2',
      'editorLineNumber.foreground': '#0d0a1a',
      'editorLineNumber.activeForeground': '#5E00A0',
      'editor.selectionHighlightBackground': '#1f1248',
      'editorBracketMatch.background': '#1f124880',
      'editorBracketMatch.border': '#7c3aed80',
      'editorRuler.foreground': '#080810',
      'editorHoverWidget.background': '#040308',
      'editorHoverWidget.border': '#0d0a1a',
    },
  })
}

export interface EditorMarker {
  line: number
  column: number
  message: string
}

interface SimplesEditorProps {
  code?: string
  onCodeChange?: (code: string) => void
  markers?: EditorMarker[]
}

export function SimplesEditor({ code, onCodeChange, markers }: SimplesEditorProps) {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null)
  const monacoRef = useRef<Parameters<OnMount>[1] | null>(null)

  const handleBeforeMount: BeforeMount = useCallback((monaco) => {
    registerSimplesLanguage(monaco)
  }, [])

  const handleMount: OnMount = useCallback((editorInstance, monacoInstance) => {
    editorRef.current = editorInstance
    monacoRef.current = monacoInstance
  }, [])

  useEffect(() => {
    const editor = editorRef.current
    const monaco = monacoRef.current
    if (!editor || !monaco) return

    const model = editor.getModel()
    if (!model) return

    if (markers && markers.length > 0) {
      monaco.editor.setModelMarkers(model, 'simples-editor', markers.map(m => ({
        severity: monaco.MarkerSeverity.Error,
        startLineNumber: m.line,
        startColumn: m.column,
        endLineNumber: m.line,
        endColumn: m.column + 20,
        message: m.message,
      })))
    } else {
      monaco.editor.setModelMarkers(model, 'simples-editor', [])
    }
  }, [markers])

  return (
    <Editor
      height="100%"
      language="simples"
      theme="simples-galaxy"
      value={code ?? DEFAULT_CODE}
      beforeMount={handleBeforeMount}
      onMount={handleMount}
      onChange={(value) => onCodeChange?.(value ?? '')}
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
