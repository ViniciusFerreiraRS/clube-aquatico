"""Interface de terminal do Clube Aquático.

Aqui fica só a conversa com o usuário (perguntas e impressão do resultado).
Todas as contas e regras estão em regras.py.
"""

import textwrap
from decimal import Decimal

from regras import (
    ErroDeValidacao,
    Resultado,
    Solicitacao,
    calcular_adesao,
    ler_inteiro,
    ler_sim_nao,
    modalidades_disponiveis,
    validar_anos_associado,
    validar_idade,
    validar_membros_familia,
    validar_nome,
)

LARGURA = 54


# ---------------------------------------------------------------------------
# Formatação
# ---------------------------------------------------------------------------
def formatar_moeda(valor: Decimal) -> str:
    """Decimal('1234.5') -> 'R$ 1.234,50'."""
    texto = f"{valor:,.2f}"  # 1,234.50
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def formatar_percentual(valor: Decimal) -> str:
    return f"{valor * 100:.0f}%"


def linha(rotulo: str, valor: str) -> str:
    """Rótulo à esquerda e valor alinhado à direita.

    Se não couber na largura da ficha (nome muito comprido, por exemplo),
    o valor desce para a linha de baixo, quebrado em várias linhas se preciso.
    """
    if len(rotulo) + len(valor) + 6 > LARGURA:
        quebrado = textwrap.fill(
            valor, width=LARGURA - 2, initial_indent="  ", subsequent_indent="  "
        )
        return f"  {rotulo}\n{quebrado}"
    return f"  {rotulo}".ljust(LARGURA - len(valor) - 2) + valor + "  "


# ---------------------------------------------------------------------------
# Perguntas
# ---------------------------------------------------------------------------
def perguntar(texto: str, converter):
    """Repete a pergunta até a resposta ser válida."""
    while True:
        resposta = input(texto)
        try:
            return converter(resposta)
        except ErroDeValidacao as erro:
            print(f"  Erro: {erro}")


def como_inteiro(campo: str, validar, *extras):
    """Monta um conversor: texto -> número inteiro -> validação do campo."""
    return lambda texto: validar(ler_inteiro(texto, campo), *extras)


def escolher_modalidade(idade: int) -> str:
    opcoes = modalidades_disponiveis(idade)
    print("\nModalidades disponíveis:")
    for numero, modalidade in enumerate(opcoes, start=1):
        extra = (
            "incluso"
            if modalidade.adicional == 0
            else f"+ {formatar_moeda(modalidade.adicional)}/mês"
        )
        print(f"  {numero}) {modalidade.nome} ({extra})")

    def converter(texto: str) -> str:
        numero = ler_inteiro(texto, "Opção")
        if not 1 <= numero <= len(opcoes):
            raise ErroDeValidacao(f"Escolha um número de 1 a {len(opcoes)}.")
        return opcoes[numero - 1].chave

    return perguntar("Escolha a modalidade: ", converter)


def coletar_dados() -> Solicitacao:
    print("\n--- Novo sócio ---")
    nome = perguntar("Nome: ", validar_nome)
    idade = perguntar("Idade: ", como_inteiro("Idade", validar_idade))
    modalidade = escolher_modalidade(idade)
    aquecida = perguntar("Piscina aquecida? (s/n): ", ler_sim_nao)
    familia = perguntar(
        "Pessoas da família no clube, contando você: ",
        como_inteiro("Pessoas da família", validar_membros_familia),
    )
    anos = perguntar(
        "Anos como sócio (0 se for novo): ",
        como_inteiro("Anos como sócio", validar_anos_associado, idade),
    )
    anual = perguntar("Pagamento anual à vista? (s/n): ", ler_sim_nao)
    return Solicitacao(nome, idade, modalidade, aquecida, familia, anos, anual)


# ---------------------------------------------------------------------------
# Saída
# ---------------------------------------------------------------------------
def exibir_resultado(r: Resultado) -> None:
    print("\n" + "=" * LARGURA)
    print("FICHA DO SÓCIO".center(LARGURA))
    print("=" * LARGURA)
    print(linha("Nome", r.nome))
    print(linha("Idade", f"{r.idade} anos"))
    print(linha("Categoria", r.categoria))
    print(linha("Modalidade", r.modalidade))

    print("-" * LARGURA)
    print(linha(f"Mensalidade {r.categoria}", formatar_moeda(r.mensalidade_base)))
    if r.adicional_modalidade > 0:
        print(linha(f"+ {r.modalidade}", formatar_moeda(r.adicional_modalidade)))
    if r.adicional_aquecida > 0:
        print(linha("+ Piscina aquecida", formatar_moeda(r.adicional_aquecida)))
    print(linha("Subtotal", formatar_moeda(r.subtotal)))

    if r.descontos:
        for desconto in r.descontos:
            print(linha(
                f"- {desconto.descricao} ({formatar_percentual(desconto.percentual)})",
                formatar_moeda(desconto.valor),
            ))
        if r.limite_aplicado:
            print(f"  Limite de {formatar_percentual(r.percentual_aplicado)} "
                  "de desconto aplicado.")
        print(linha(
            f"Desconto total ({formatar_percentual(r.percentual_aplicado)})",
            "- " + formatar_moeda(r.desconto_total),
        ))
    else:
        print("  Nenhum desconto aplicável.")

    print("-" * LARGURA)
    print(linha("TOTAL MENSAL", formatar_moeda(r.total_mensal)))
    if r.total_anual is not None:
        print(linha("TOTAL ANUAL (12 meses)", formatar_moeda(r.total_anual)))

    print("-" * LARGURA)
    print("  Permissões de uso")
    print("  Piscinas liberadas:")
    for piscina in r.piscinas:
        print(f"    - {piscina}")
    print(f"  Horário      : {r.horario}")
    acompanhante = "obrigatório (responsável adulto)" if r.exige_acompanhante else "não exige"
    print(f"  Acompanhante : {acompanhante}")
    print("=" * LARGURA)


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * LARGURA)
    print("CLUBE AQUÁTICO - Cadastro de sócios".center(LARGURA))
    print("=" * LARGURA)
    try:
        while True:
            exibir_resultado(calcular_adesao(coletar_dados()))
            if not perguntar("\nCadastrar outro sócio? (s/n): ", ler_sim_nao):
                break
    except (EOFError, KeyboardInterrupt):
        print()
    print("Encerrado. Até logo!")


if __name__ == "__main__":
    main()
