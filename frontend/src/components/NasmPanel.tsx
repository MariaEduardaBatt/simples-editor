import { useCallback, useRef } from 'react'
import type { editor } from 'monaco-editor'
import Editor, { type BeforeMount, type OnMount } from '@monaco-editor/react'

const NASM_INSTRUCTIONS = [
  "aaa", "aad", "aam", "aas", "adc", "add", "and", "call", "cbw", "clc",
  "cld", "cli", "cmc", "cmp", "cmpsb", "cmpsw", "cmpsd", "cwd", "cdq",
  "daa", "das", "dec", "div", "enter", "hlt", "idiv", "imul", "in",
  "inc", "insb", "insw", "insd", "int", "into", "iret", "jmp", "ja",
  "jae", "jb", "jbe", "jc", "jcxz", "jecxz", "je", "jg", "jge", "jl",
  "jle", "jna", "jnae", "jnb", "jnbe", "jnc", "jne", "jng", "jnge",
  "jnl", "jnle", "jno", "jnp", "jns", "jnz", "jo", "jp", "jpe", "jpo",
  "js", "jz", "lahf", "lds", "lea", "les", "lfs", "lgs", "lss", "lock",
  "lodsb", "lodsw", "lodsd", "loop", "loope", "loopne", "loopnz",
  "loopz", "mov", "movsb", "movsw", "movsd", "mul", "neg", "nop",
  "not", "or", "out", "outsb", "outsw", "outsd", "pop", "popa", "popad",
  "popf", "popfd", "push", "pusha", "pushad", "pushf", "pushfd", "rcl",
  "rcr", "ret", "retf", "retn", "rol", "ror", "sahf", "sal", "sar",
  "shl", "shr", "sbb", "scasb", "scasw", "scasd", "sete", "setne",
  "setz", "setnz", "sets", "setns", "setg", "setge", "setl", "setle",
  "seta", "setae", "setb", "setbe", "setc", "setnc", "seto", "setno",
  "setp", "setpe", "setnp", "setpo", "sgdt", "sidt", "sldt", "shld",
  "shrd", "smsl", "smsw", "stc", "std", "sti", "stosb", "stosw",
  "stosd", "str", "sub", "test", "verr", "verw", "wait", "xchg",
  "xlat", "xlatb", "xor",
] as const

const NASM_REGISTERS = [
  "eax", "ebx", "ecx", "edx", "esi", "edi", "esp", "ebp", "eip",
  "ax", "bx", "cx", "dx", "si", "di", "sp", "bp",
  "ah", "al", "bh", "bl", "ch", "cl", "dh", "dl",
  "cr0", "cr1", "cr2", "cr3", "cr4",
  "db0", "db1", "db2", "db3", "db4", "db5", "db6", "db7",
  "dr0", "dr1", "dr2", "dr3", "dr4", "dr5", "dr6", "dr7",
  "st0", "st1", "st2", "st3", "st4", "st5", "st6", "st7",
  "mm0", "mm1", "mm2", "mm3", "mm4", "mm5", "mm6", "mm7",
  "xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7",
  "cs", "ds", "es", "fs", "gs", "ss",
] as const

const NASM_DIRECTIVES = [
  "section", "segment", "global", "extern", "common", "cpu",
  "bits", "org", "align", "alignb", "sectalign",
  "db", "dw", "dd", "dq", "dt", "do", "dy", "dz",
  "resb", "resw", "resd", "resq", "rest", "reso", "resy", "resz",
  "incbin", "equ", "times", "struc", "endstruc", "istruc", "at", "iend",
  "macro", "endmacro", "imacro", "iendmacro",
] as const

const NASM_SIZES = [
  "byte", "word", "dword", "qword", "tword", "oword", "yword", "zword",
  "ptr", "short", "near", "far",
] as const

const DEFAULT_NASM = `; exemplo - SIMPLES -> NASM x32
section .data
  msg db "Hello, SIMPLES!", 0xA, 0
  fmt db "%s", 0

section .text
  global _start

_start:
  ; escreva "Hello, SIMPLES!"
  push msg
  push fmt
  call printf
  add esp, 8

  ; fim
  mov eax, 1
  xor ebx, ebx
  int 0x80`

function registerNasmLanguage(monaco: Parameters<BeforeMount>[0]) {
  monaco.languages.register({ id: 'nasm' })

  monaco.languages.setMonarchTokensProvider('nasm', {
    ignoreCase: true,
    instructions: NASM_INSTRUCTIONS,
    registers: NASM_REGISTERS,
    directives: NASM_DIRECTIVES,
    sizes: NASM_SIZES,
    tokenizer: {
      root: [
        [/;[^\n]*$/, 'comment'],
        [/^\s*[a-zA-Z_.][a-zA-Z0-9_.$]*:/, 'type.identifier'],
        [/[a-zA-Z_.][a-zA-Z0-9_.$]*:/, 'type.identifier'],
        [/[a-zA-Z_.][a-zA-Z0-9_.$]*/, {
          cases: {
            '@directives': 'keyword.directive',
            '@instructions': 'keyword.instruction',
            '@registers': 'variable.register',
            '@sizes': 'keyword.size',
            '@default': 'identifier',
          }
        }],
        [/\d+[hH]/, 'number.hex'],
        [/0[xX][0-9a-fA-F]+/, 'number.hex'],
        [/\d+[qQoO]/, 'number.octal'],
        [/[0-7]+[qQoO]/, 'number.octal'],
        [/\d+[bB]/, 'number.binary'],
        [/0[bB][01]+/, 'number.binary'],
        [/\d+\.\d*([eE][+-]?\d+)?/, 'number.float'],
        [/\d+/, 'number'],
        [/[<>[\](),+\-*:./\\%]/, 'delimiter'],
        [/"[^"]*"/, 'string'],
        [/'(?:[^'\\]|\\.)*'/, 'string'],
        [/[a-zA-Z_]\w*/, 'identifier'],
        [/\s+/, 'white'],
      ],
    },
  })

  monaco.editor.defineTheme('nasm-galaxy', {
    base: 'vs-dark',
    inherit: true,
    rules: [
      { token: 'keyword.instruction', foreground: '22d3ee', fontStyle: 'bold' },
      { token: 'keyword.directive', foreground: 'a78bfa' },
      { token: 'keyword.size', foreground: 'fbbf24' },
      { token: 'variable.register', foreground: '5E00A0', fontStyle: 'bold' },
      { token: 'type.identifier', foreground: '34d399' },
      { token: 'number', foreground: 'fbbf24' },
      { token: 'number.hex', foreground: 'f472b6' },
      { token: 'number.octal', foreground: 'f472b6' },
      { token: 'number.binary', foreground: 'f472b6' },
      { token: 'number.float', foreground: 'fbbf24' },
      { token: 'string', foreground: '67e8f9' },
      { token: 'delimiter', foreground: 'e2e8f0' },
      { token: 'identifier', foreground: 'f1f5f9' },
      { token: 'comment', foreground: '4a5568', fontStyle: 'italic' },
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

interface NasmPanelProps {
  code?: string
  isCompiling?: boolean
}

export function NasmPanel({ code, isCompiling = false }: NasmPanelProps) {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null)

  const handleBeforeMount: BeforeMount = useCallback((monaco) => {
    registerNasmLanguage(monaco)
  }, [])

  const handleMount: OnMount = useCallback((editorInstance) => {
    editorRef.current = editorInstance
  }, [])

  const value = code ?? (isCompiling ? '' : DEFAULT_NASM)

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-white/[0.06] px-4 py-2">
        <span className="text-xs font-medium uppercase tracking-wider text-white/40">
          NASM x32
        </span>
        <span className="rounded-md border border-white/[0.06] bg-white/[0.03] px-2 py-0.5 text-[10px] text-white/30">
          read-only
        </span>
      </div>
      <div className="relative flex min-h-0 flex-1">
        {isCompiling && !code && (
          <div className="absolute inset-0 z-10 flex items-center justify-center bg-[#0a0a0f]">
            <div className="text-center">
              <p className="text-sm text-nebula-400">compilando...</p>
            </div>
          </div>
        )}
        <Editor
          height="100%"
          language="nasm"
          theme="nasm-galaxy"
          value={value}
          beforeMount={handleBeforeMount}
          onMount={handleMount}
          loading={
            <div className="flex h-full items-center justify-center">
              <div className="text-center">
                <p className="text-sm text-white/20">Carregando editor...</p>
              </div>
            </div>
          }
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
            readOnly: true,
            domReadOnly: true,
            cursorStyle: 'line-thin',
            cursorWidth: 1,
          }}
        />
      </div>
    </div>
  )
}
