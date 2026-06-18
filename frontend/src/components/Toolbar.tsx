import { useEffect, useRef, useState } from 'react'

interface Example {
  name: string
  code: string
}

const EXAMPLES: Example[] = [
  {
    name: 'Olá Mundo',
    code: `programa hello
inicio
  escreval "Ola, mundo!"
fim`,
  },
  {
    name: 'Fatorial',
    code: `procedimento inteiro fatorial(inteiro n)
inicio
  inteiro i, resultado
  resultado <- 1
  para i de 2 ate n passo 1 faca
    resultado <- resultado * i
  fimpara
  retorna resultado
fim

programa demo
inteiro x
inicio
  escreva "digite um numero: "
  leia x
  escreva "fatorial de "
  escreva x
  escreva " = "
  escreval fatorial(x)
fim`,
  },
  {
    name: 'Fibonacci',
    code: `procedimento inteiro fibonacci(inteiro n)
inicio
  inteiro i, a, b, tmp
  a <- 0
  b <- 1
  se n = 0 entao
    retorna 0
  senao
    se n = 1 entao
      retorna 1
    senao
      para i de 2 ate n passo 1 faca
        tmp <- a + b
        a <- b
        b <- tmp
      fimpara
      retorna b
    fimse
  fimse
fim

programa demo
inteiro n, i
inicio
  escreva "digite um numero: "
  leia n
  se n > 46 entao
    escreval "numero muito grande"
  senao
    escreva "fibonacci ate "
    escreva n
    escreval ":"
    para i de 0 ate n passo 1 faca
      escreva fibonacci(i)
      se i < n entao
        escreva " "
      fimse
    fimpara
    escreval ""
  fimse
fim`,
  },
  {
    name: 'Tabuada',
    code: `programa tabuada
inteiro i, j
inicio
  para i de 1 ate 10 passo 1 faca
    para j de 1 ate 10 passo 1 faca
      escreva i * j
      escreva " "
    fimpara
  escreval ""
  fimpara
fim`,
  },
]

interface ToolbarProps {
  code?: string
  onRun?: (code: string) => void
  onStop?: () => void
  isRunning: boolean
  onClear?: () => void
  onExampleSelect?: (code: string) => void
}

export function Toolbar({ code, onRun, onStop, isRunning, onClear, onExampleSelect }: ToolbarProps) {
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!dropdownOpen) return
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [dropdownOpen])

  function handleRun() {
    const source = code ?? ''
    onRun?.(source)
  }

  function handleExampleClick(example: Example) {
    onExampleSelect?.(example.code)
    setDropdownOpen(false)
  }

  return (
    <div className="mx-6 flex items-center gap-3">
      <button
        className="flex items-center gap-2 rounded-xl border border-nebula-500/30 bg-nebula-500/10 px-5 py-2 text-sm font-medium text-nebula-300 transition enabled:border-nebula-400/60 enabled:bg-nebula-500/20 enabled:text-nebula-200 enabled:hover:bg-nebula-500/30 enabled:hover:text-nebula-100 disabled:cursor-not-allowed disabled:opacity-50"
        type="button"
        onClick={handleRun}
        disabled={isRunning}
      >
        <span className="text-base leading-none">{isRunning ? '◌' : '▶'}</span>
        {isRunning ? 'executando…' : 'Run'}
      </button>
      <button
        className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-white/40 transition enabled:border-red-500/50 enabled:bg-red-500/10 enabled:text-red-300 enabled:hover:border-red-400 enabled:hover:bg-red-500/20 enabled:hover:text-red-200 disabled:opacity-30"
        type="button"
        onClick={onStop}
        disabled={!isRunning}
      >
        <span className="text-base leading-none">■</span>
        Stop
      </button>
      <button
        className="rounded-xl border border-white/[0.06] bg-white/[0.02] px-4 py-2 text-sm text-white/30 transition hover:border-white/10 hover:text-white/50"
        type="button"
        onClick={onClear}
      >
        Limpar
      </button>

      <div ref={dropdownRef} className="relative ml-auto">
        <button
          className="flex items-center gap-1 rounded-xl border border-white/[0.06] bg-white/[0.02] px-4 py-2 text-sm text-white/30 transition hover:border-white/10 hover:text-white/50"
          type="button"
          onClick={() => setDropdownOpen((v) => !v)}
        >
          exemplos
          <svg className={`h-3 w-3 transition ${dropdownOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        {dropdownOpen && (
          <div className="absolute right-0 top-full z-50 mt-2 w-52 overflow-hidden rounded-xl border border-white/[0.08] bg-[#0a0a0f] shadow-xl shadow-black/40">
            {EXAMPLES.map((ex) => (
              <button
                key={ex.name}
                className="block w-full px-4 py-2.5 text-left text-sm text-white/50 transition hover:bg-white/[0.04] hover:text-white/80"
                type="button"
                onClick={() => handleExampleClick(ex)}
              >
                {ex.name}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
