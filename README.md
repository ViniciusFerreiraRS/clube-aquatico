# Clube Aquático

Sistema de terminal em Python que registra a adesão de novos sócios de um clube
aquático: define a categoria pela idade, calcula a mensalidade com adicionais e
descontos e mostra o que o sócio pode usar no clube.

> Projeto de estudo. As regras (categorias, valores, descontos) são fictícias e
> foram inventadas para praticar lógica de programação e organização de código.

## Objetivo

Transformar um exercício simples de "ler dados, fazer contas e mostrar o resultado" em um projeto mais completo, seguindo etapas comuns do desenvolvimento de software: entender o problema, organizar as regras, programar, testar, melhorar o código e documentar.

## Desenvolvimento assistido por IA

Este é um **projeto de estudo desenvolvido com auxílio de inteligência artificial**.

A IA foi utilizada como ferramenta de apoio na criação, revisão, documentação e evolução do projeto. A partir da estrutura inicial, o código está sendo utilizado como laboratório de aprendizagem, sendo lido, executado, testado e modificado ao longo dos estudos.

O objetivo é compreender as decisões técnicas, realizar alterações próprias e registrar essa evolução no histórico do Git.

Neste repositório, a inteligência artificial é tratada como **ferramenta de apoio ao desenvolvimento (AI-assisted development)**, e não como substituta do aprendizado.

### Participação no projeto

- **Claude Code** — apoio na criação da estrutura inicial, geração de partes do código, testes e documentação.
- **ChatGPT (OpenAI)** — apoio na revisão do projeto, organização da documentação, orientação sobre Git/GitHub e planejamento das melhorias.
- **Vinicius Moreira Ferreira** — responsável pelo projeto de estudo, pelas decisões de aprendizado, revisão, compreensão do código e evolução progressiva do sistema.
- **Objetivo atual** — estudar o código existente, compreender seu funcionamento e realizar melhorias progressivas.

> O termo informal **vibe coding** pode descrever parte do processo de prototipação, mas neste projeto é utilizado o termo **desenvolvimento assistido por IA**, por representar melhor o papel das ferramentas e o objetivo de aprendizagem.
## Estrutura do projeto

```text
clube_aquatico/
├── README.md
├── .gitignore
├── docs/
│   ├── requisitos.md           # Etapa 1: quem usa, o que faz, entradas e saídas
│   └── regras_de_negocio.md    # Etapa 2: todas as regras em tabelas
├── src/
│   ├── regras.py               # Validações e cálculos (sem print/input)
│   └── main.py                 # Conversa com o usuário no terminal
└── tests/
    └── test_regras.py          # 44 testes automatizados
```

## Regras de funcionamento

Resumo (o detalhamento completo está em
[docs/regras_de_negocio.md](docs/regras_de_negocio.md)).

**Categorias e mensalidade base**

| Categoria | Idades | Mensalidade |
|---|---|---|
| Infantil | 4 a 12 | R$ 80,00 |
| Juvenil | 13 a 17 | R$ 100,00 |
| Adulto | 18 a 59 | R$ 150,00 |
| Sênior | 60 a 110 | R$ 110,00 |

**Adicionais (por mês)**

| Item | Valor | Quem pode |
|---|---|---|
| Uso livre | incluso | todos |
| Aulas de natação | + R$ 60,00 | todos |
| Hidroginástica | + R$ 50,00 | 18 anos ou mais |
| Equipe de competição | + R$ 90,00 | 8 a 59 anos |
| Piscina aquecida | + R$ 25,00 | todos |

**Descontos** (somados e aplicados sobre o subtotal, com **teto de 25%**)

| Desconto | Condição | Percentual |
|---|---|---|
| Família | 2 pessoas / 3 ou mais | 10% / 15% |
| Tempo de sócio | 5 a 9 anos / 10 anos ou mais | 5% / 10% |
| Pagamento anual à vista | escolhido | 10% |

**Permissões de uso**

| Categoria | Horário | Acompanhante |
|---|---|---|
| Infantil | 08h às 18h | obrigatório |
| Juvenil | 06h às 21h | não |
| Adulto e Sênior | 06h às 22h | não |

## Como executar

Precisa apenas do Python 3.9 ou superior. Não há nada para instalar.

```bash
python3 src/main.py
```

Para rodar os testes:

```bash
python3 -m unittest discover -s tests -v
```

## Exemplos de entrada e saída

### 1. Adulta com vários descontos (o teto de 25% entra em ação)

Entradas: `Ana Souza`, `35`, modalidade `2` (natação), aquecida `s`, família `3`,
anos como sócia `6`, pagamento anual `s`.

```text
======================================================
                    FICHA DO SÓCIO                    
======================================================
  Nome                                     Ana Souza  
  Idade                                      35 anos  
  Categoria                                   Adulto  
  Modalidade                        Aulas de natação  
------------------------------------------------------
  Mensalidade Adulto                       R$ 150,00  
  + Aulas de natação                        R$ 60,00  
  + Piscina aquecida                        R$ 25,00  
  Subtotal                                 R$ 235,00  
  - Família, 3 pessoas (15%)                R$ 35,25  
  - Tempo de sócio, 6 anos (5%)             R$ 11,75  
  - Pagamento anual à vista (10%)           R$ 23,50  
  Limite de 25% de desconto aplicado.
  Desconto total (25%)                    - R$ 58,75  
------------------------------------------------------
  TOTAL MENSAL                             R$ 176,25  
  TOTAL ANUAL (12 meses)                 R$ 2.115,00  
------------------------------------------------------
  Permissões de uso
  Piscinas liberadas:
    - Piscina recreativa
    - Piscina semiolímpica
    - Piscina aquecida
  Horário      : 06h às 22h
  Acompanhante : não exige
======================================================
```

Os três descontos somariam 30%, mas o teto é 25%: 25% de R$ 235,00 = R$ 58,75.

### 2. Criança (acompanhante obrigatório)

```text
--- Novo sócio ---
Nome: Lia
Idade: 6

Modalidades disponíveis:
  1) Uso livre (incluso)
  2) Aulas de natação (+ R$ 60,00/mês)
Escolha a modalidade: 2
Piscina aquecida? (s/n): n
Pessoas da família no clube, contando você: 2
Anos como sócio (0 se for novo): 0
Pagamento anual à vista? (s/n): n

======================================================
                    FICHA DO SÓCIO                    
======================================================
  Nome                                           Lia  
  Idade                                       6 anos  
  Categoria                                 Infantil  
  Modalidade                        Aulas de natação  
------------------------------------------------------
  Mensalidade Infantil                      R$ 80,00  
  + Aulas de natação                        R$ 60,00  
  Subtotal                                 R$ 140,00  
  - Família, 2 pessoas (10%)                R$ 14,00  
  Desconto total (10%)                    - R$ 14,00  
------------------------------------------------------
  TOTAL MENSAL                             R$ 126,00  
------------------------------------------------------
  Permissões de uso
  Piscinas liberadas:
    - Piscina infantil
    - Piscina recreativa
  Horário      : 08h às 18h
  Acompanhante : obrigatório (responsável adulto)
======================================================
```

Como a Lia tem 6 anos, o menu nem oferece hidroginástica nem equipe de competição.

### 3. Entradas inválidas (o programa pergunta de novo, sem quebrar)

```text
--- Novo sócio ---
Nome: 
  Erro: Nome: informe pelo menos 2 caracteres.
Nome: Carlos
Idade: 3
  Erro: Idade: o clube só aceita sócios a partir de 4 anos.
Idade: abc
  Erro: Idade: digite um número inteiro (você digitou 'abc').
Idade: 17

Modalidades disponíveis:
  1) Uso livre (incluso)
  2) Aulas de natação (+ R$ 60,00/mês)
  3) Equipe de competição (+ R$ 90,00/mês)
Escolha a modalidade: 9
  Erro: Escolha um número de 1 a 3.
Escolha a modalidade: 1
Piscina aquecida? (s/n): talvez
  Erro: Responda com 's' para sim ou 'n' para não.
Piscina aquecida? (s/n): n
Pessoas da família no clube, contando você: 0
  Erro: Pessoas da família: o mínimo é 1 (o próprio candidato conta).
Pessoas da família no clube, contando você: 1
Anos como sócio (0 se for novo): 20
  Erro: Anos como sócio: com 17 anos de idade, o máximo possível é 13 (o clube só aceita sócios a partir de 4 anos).
Anos como sócio (0 se for novo): 0
Pagamento anual à vista? (s/n): n
```

## Testes

São 44 testes com `unittest` (biblioteca padrão), cobrindo:

- **Categorias:** todas as bordas de idade (4, 12, 13, 17, 18, 59, 60, 110) e um teste
  que garante que a tabela cobre todas as idades sem buracos nem sobreposição.
- **Valores:** mínimo (criança de 4 anos), cada modalidade e adicional.
- **Descontos:** cada faixa, as bordas (4/5/9/10 anos de sócio), o teto de 25% e o
  caso exato de 25% (que não conta como "limite aplicado").
- **Entradas inválidas:** idade fora da faixa ou de tipo errado, nome vazio ou longo
  demais, família 0 ou 21, anos de sócio negativos ou impossíveis, texto no lugar de número.
- **Terminal de ponta a ponta:** fluxo completo, repetição de pergunta após erro,
  dois sócios na mesma execução, nome comprido e fim da entrada (Ctrl+D).

Além de passarem, os testes foram verificados quebrando 10 regras de propósito
numa cópia (por exemplo, trocar o teto de 25% por 30%): todas foram detectadas.

## Decisões de projeto

- **`Decimal` em vez de `float`** para dinheiro, evitando erros de centavos.
- **Regras separadas da interface:** `regras.py` não usa `print` nem `input`,
  por isso é testado sem simular o terminal.
- **Valores em constantes e tabelas** no topo de `regras.py`: mudar uma regra
  significa mudar um valor num só lugar.
- **Validação em um só lugar:** o terminal e `calcular_adesao()` usam as mesmas
  funções de validação, então a regra não pode divergir entre as duas.

## O que este projeto pratica

- Levantar requisitos e transformar um enunciado em regras objetivas antes de programar.
- Separar lógica de negócio e interface.
- Tratar entrada inválida e casos de borda.
- Escrever testes que realmente detectam erros, e não só passam.
- Documentar para outra pessoa conseguir rodar e entender.

## Possíveis melhorias

- Salvar os cadastros em arquivo CSV ou JSON.
- Interface web simples ou versão com menu de renovação de plano.
- Regras de preço lidas de um arquivo de configuração em vez de constantes no código.
