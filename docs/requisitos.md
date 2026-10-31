# Etapa 1 — Requisitos do Clube Aquático

## 1. Contexto

Sistema de terminal que registra a **adesão de novos sócios** de um clube aquático.
A partir dos dados do candidato, ele define a categoria, calcula a mensalidade
(com adicionais e descontos) e informa o que o sócio pode usar no clube.

> As regras deste projeto são fictícias e foram criadas para estudo/portfólio.

## 2. Quem usa o sistema

| Ator | O que faz |
|---|---|
| Atendente da secretaria | Digita os dados do candidato e lê o resultado. Usuário principal. |
| Sócio ou responsável | Recebe o resumo com valor e permissões de uso. Não opera o sistema. |

## 3. O que o sistema precisa fazer (requisitos funcionais)

| ID | Requisito |
|---|---|
| RF01 | Ler os dados do candidato pelo terminal. |
| RF02 | Validar cada dado e pedir de novo quando estiver inválido, sem encerrar o programa. |
| RF03 | Definir a categoria (Infantil, Juvenil, Adulto, Sênior) a partir da idade. |
| RF04 | Calcular a mensalidade base da categoria mais os adicionais escolhidos. |
| RF05 | Aplicar descontos (família, tempo de sócio, pagamento anual) respeitando o teto de 25%. |
| RF06 | Mostrar o total mensal e, no pagamento anual, o total do ano. |
| RF07 | Mostrar as permissões de uso: piscinas, horário e se exige acompanhante. |
| RF08 | Permitir cadastrar vários sócios na mesma execução. |
| RF09 | Impedir combinações proibidas (por exemplo, hidroginástica para menor de 18 anos). |

## 4. Requisitos não funcionais

- Python 3.9 ou superior, **sem bibliotecas externas**.
- Valores em dinheiro com `Decimal`, nunca `float`, para evitar erros de centavos.
- Regras de negócio separadas da interface (`regras.py` não usa `print` nem `input`).
- Testes automatizados com `unittest`.
- Mensagens de erro claras, em português.

## 5. Entradas

| Campo | Tipo | Exemplo |
|---|---|---|
| Nome | texto | Ana Souza |
| Idade | inteiro | 35 |
| Modalidade | escolha de uma lista | Aulas de natação |
| Piscina aquecida | sim/não | s |
| Pessoas da família no clube (contando o candidato) | inteiro | 3 |
| Anos como sócio (0 se for novo) | inteiro | 6 |
| Pagamento anual à vista | sim/não | s |

## 6. Saídas

- Ficha com nome, idade e categoria.
- Detalhamento do valor: base, adicionais, subtotal, cada desconto, total mensal.
- Total anual, quando o pagamento for anual.
- Permissões: piscinas liberadas, horário e acompanhante.

## 7. Fora do escopo

Banco de dados, login, pagamento real, interface gráfica e gravação dos cadastros.
