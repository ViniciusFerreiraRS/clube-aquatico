# Etapa 2 — Regras de negócio

Todas as regras ficam em `src/regras.py`, em constantes no topo do arquivo.
Para mudar um valor, basta alterar a constante.

## 1. Cadastro (validações)

| Campo | Regra |
|---|---|
| Nome | Obrigatório, de 2 a 80 caracteres, sem espaços sobrando nas pontas. |
| Idade | Inteiro entre 4 e 110. Menores de 4 anos não podem se associar. |
| Modalidade | Precisa existir e respeitar a faixa de idade dela (seção 5). |
| Pessoas da família | Inteiro de 1 a 20 (o próprio candidato conta). |
| Anos como sócio | Inteiro ≥ 0 e que não ultrapasse `idade - 4` (ninguém é sócio antes de ter 4 anos). |
| Sim/não | Aceita `s`, `sim`, `n`, `nao`, `não` (maiúsculas ou minúsculas). |

## 2. Idade e categoria

| Categoria | Idades | Mensalidade base |
|---|---|---|
| Infantil | 4 a 12 | R$ 80,00 |
| Juvenil | 13 a 17 | R$ 100,00 |
| Adulto | 18 a 59 | R$ 150,00 |
| Sênior | 60 a 110 | R$ 110,00 |

## 3. Valor (adicionais)

| Item | Valor mensal | Quem pode |
|---|---|---|
| Uso livre | incluso | todos |
| Aulas de natação | + R$ 60,00 | todos |
| Hidroginástica | + R$ 50,00 | 18 anos ou mais |
| Equipe de competição | + R$ 90,00 | 8 a 59 anos |
| Piscina aquecida (opcional) | + R$ 25,00 | todos |

**Subtotal** = mensalidade base + modalidade + piscina aquecida.

## 4. Descontos

Todos incidem sobre o subtotal e são **somados**.

| Desconto | Condição | Percentual |
|---|---|---|
| Família | 2 pessoas | 10% |
| Família | 3 ou mais | 15% |
| Tempo de sócio | 5 a 9 anos | 5% |
| Tempo de sócio | 10 anos ou mais | 10% |
| Pagamento anual à vista | escolhido | 10% |

**Teto:** a soma dos descontos nunca passa de **25%**.
O valor final é arredondado para centavos (meio para cima).

**Total anual** (só no pagamento anual) = total mensal × 12.

## 5. Permissões de uso

| Categoria | Piscinas | Horário | Acompanhante |
|---|---|---|---|
| Infantil | Infantil, Recreativa | 08h às 18h | Obrigatório (responsável adulto) |
| Juvenil | Recreativa, Semiolímpica | 06h às 21h | Não |
| Adulto | Recreativa, Semiolímpica | 06h às 22h | Não |
| Sênior | Recreativa, Semiolímpica | 06h às 22h | Não |

Com a opção **piscina aquecida**, a "Piscina aquecida" é acrescentada à lista.

## 6. Exemplo calculado à mão (usado nos testes)

Ana, 35 anos, natação, piscina aquecida, 3 na família, 6 anos de sócia, pagamento anual:

- Subtotal: 150,00 + 60,00 + 25,00 = **235,00**
- Descontos: 15% + 5% + 10% = 30% → passa do teto, vale **25%**
- Desconto: 235,00 × 25% = 58,75
- Total mensal: **176,25**
- Total anual: 176,25 × 12 = **2.115,00**
