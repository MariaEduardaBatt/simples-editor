export interface Example {
  name: string
  label: string
  code: string
}

const hello: Example = {
  name: 'hello',
  label: 'Hello World',
  code: `programa hello
inicio
  escreval "Ola, mundo!";
fim`,
}

const fatorial: Example = {
  name: 'fatorial',
  label: 'Fatorial',
  code: `procedimento inteiro fatorial(inteiro n)
inicio
  inteiro i, resultado;
  resultado <- 1;
  para i de 2 ate n passo 1 faca
    resultado <- resultado * i;
  fimpara
  retorna resultado;
fim

programa demo
inteiro x;
inicio
  escreva "digite o numero: ";
  leia x;
  escreva "fatorial de ";
  escreva x;
  escreva " = ";
  escreval fatorial(x);
fim`,
}

const fibonacci: Example = {
  name: 'fibonacci',
  label: 'Fibonacci',
  code: `procedimento inteiro fibonacci(inteiro n)
inicio
  inteiro i, a, b, tmp;
  a <- 0;
  b <- 1;
  se n = 0 entao
    retorna 0;
  senao
    se n = 1 entao
      retorna 1;
    senao
      para i de 2 ate n passo 1 faca
        tmp <- a + b;
        a <- b;
        b <- tmp;
      fimpara
      retorna b;
    fimse
  fimse
fim

programa demo
inteiro n, i;
inicio
  escreva "digite o numero: ";
  leia n;
  se n > 46 entao
    escreval "numero muito grande";
  senao
    escreva "fibonacci ate ";
    escreva n;
    escreval ":";
    para i de 0 ate n passo 1 faca
      escreva fibonacci(i);
      se i < n entao
        escreva " ";
      fimse
    fimpara
    escreval "";
  fimse
fim`,
}

const tabuada: Example = {
  name: 'tabuada',
  label: 'Tabuada',
  code: `programa tabuada
inteiro n, i;
inicio
  escreva "digite um numero: ";
  leia n;
  para i de 1 ate 10 passo 1 faca
    escreva n;
    escreva " x ";
    escreva i;
    escreva " = ";
    escreval n * i;
  fimpara
fim`,
}

const ifExample: Example = {
  name: 'if',
  label: 'Se / Entao / Senao',
  code: `programa demo
inteiro x;
inicio
  x <- -1;
  se x > 0 entao
    escreval x;
  senao
    escreval 0;
  fimse
fim`,
}

const forExample: Example = {
  name: 'for',
  label: 'Para (for)',
  code: `programa demo
inteiro i, total;
inicio
  total <- 0;
  para i de 1 ate 5 passo 1 faca
    total <- total + i;
  fimpara
  escreval total;
fim`,
}

const whileExample: Example = {
  name: 'while',
  label: 'Enquanto (while)',
  code: `programa demo
inteiro x;
inicio
  x <- 0;
  enquanto x < 3 faca
    x <- x + 1;
    escreva x;
  fimenquanto
fim`,
}

const readExample: Example = {
  name: 'read',
  label: 'Leia / Escreva',
  code: `programa demo
inteiro x;
inicio
  escreva "digite um numero: ";
  leia x;
  escreval "voce digitou: ", x;
fim`,
}

const stringEcho: Example = {
  name: 'string',
  label: 'String',
  code: `programa demo
string nome[16];
inicio
  escreva "digite seu nome: ";
  leia nome;
  escreval "ola, ", nome;
fim`,
}

const vectorSum: Example = {
  name: 'vector',
  label: 'Vetor',
  code: `programa demo
inteiro nums[4], i, total;
inicio
  nums[0] <- 1;
  nums[1] <- 2;
  nums[2] <- 3;
  nums[3] <- 4;
  total <- 0;
  para i de 0 ate 3 passo 1 faca
    total <- total + nums[i];
  fimpara
  escreval total;
fim`,
}

const determinante2x2: Example = {
  name: 'determinante',
  label: 'Matriz 2x2',
  code: `procedimento inteiro determinante2(inteiro m[2][2])
inicio
  retorna m[0][0] * m[1][1] - m[0][1] * m[1][0];
fim

programa demo
inteiro m[2][2], d;
inicio
  m[0][0] <- 1;
  m[0][1] <- 2;
  m[1][0] <- 3;
  m[1][1] <- 4;

  d <- determinante2(m);
  escreval d;
fim`,
}

export const EXAMPLES: Example[] = [
  hello,
  fatorial,
  fibonacci,
  tabuada,
  ifExample,
  forExample,
  whileExample,
  readExample,
  stringEcho,
  vectorSum,
  determinante2x2,
]
