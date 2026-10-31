"""Regras de negócio do Clube Aquático.

Este módulo não usa print() nem input(): ele só valida dados, calcula valores
e devolve resultados. Por isso pode ser testado sem o terminal.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

# ---------------------------------------------------------------------------
# Constantes: toda regra "em número" fica aqui, num só lugar
# ---------------------------------------------------------------------------
IDADE_MINIMA = 4
IDADE_MAXIMA = 110
MAX_MEMBROS_FAMILIA = 20
LIMITE_DESCONTO = Decimal("0.25")  # a soma dos descontos nunca passa de 25%
DESCONTO_PAGAMENTO_ANUAL = Decimal("0.10")
ADICIONAL_PISCINA_AQUECIDA = Decimal("25.00")
MESES_NO_ANO = 12
PISCINA_AQUECIDA = "Piscina aquecida"


class ErroDeValidacao(ValueError):
    """Dado de entrada inválido. A mensagem já está pronta para o usuário."""


# ---------------------------------------------------------------------------
# Tabelas de regras
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Categoria:
    nome: str
    idade_min: int
    idade_max: int
    mensalidade: Decimal
    piscinas: tuple[str, ...]
    hora_abre: int
    hora_fecha: int
    exige_acompanhante: bool


CATEGORIAS = (
    Categoria("Infantil", 4, 12, Decimal("80.00"),
              ("Piscina infantil", "Piscina recreativa"), 8, 18, True),
    Categoria("Juvenil", 13, 17, Decimal("100.00"),
              ("Piscina recreativa", "Piscina semiolímpica"), 6, 21, False),
    Categoria("Adulto", 18, 59, Decimal("150.00"),
              ("Piscina recreativa", "Piscina semiolímpica"), 6, 22, False),
    Categoria("Sênior", 60, IDADE_MAXIMA, Decimal("110.00"),
              ("Piscina recreativa", "Piscina semiolímpica"), 6, 22, False),
)


@dataclass(frozen=True)
class Modalidade:
    chave: str
    nome: str
    adicional: Decimal
    idade_min: int
    idade_max: int


MODALIDADES = (
    Modalidade("livre", "Uso livre", Decimal("0.00"), IDADE_MINIMA, IDADE_MAXIMA),
    Modalidade("natacao", "Aulas de natação", Decimal("60.00"), IDADE_MINIMA, IDADE_MAXIMA),
    Modalidade("hidro", "Hidroginástica", Decimal("50.00"), 18, IDADE_MAXIMA),
    Modalidade("equipe", "Equipe de competição", Decimal("90.00"), 8, 59),
)


# ---------------------------------------------------------------------------
# Estruturas de entrada e saída
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Solicitacao:
    """Dados que a secretaria digita para um candidato."""
    nome: str
    idade: int
    modalidade: str            # chave da modalidade, ex.: "natacao"
    piscina_aquecida: bool
    membros_familia: int       # contando o próprio candidato
    anos_associado: int        # 0 se for sócio novo
    pagamento_anual: bool


@dataclass(frozen=True)
class Desconto:
    descricao: str
    percentual: Decimal
    valor: Decimal


@dataclass(frozen=True)
class Resultado:
    nome: str
    idade: int
    categoria: str
    modalidade: str
    mensalidade_base: Decimal
    adicional_modalidade: Decimal
    adicional_aquecida: Decimal
    subtotal: Decimal
    descontos: tuple[Desconto, ...]
    percentual_aplicado: Decimal
    limite_aplicado: bool
    desconto_total: Decimal
    total_mensal: Decimal
    total_anual: Optional[Decimal]
    piscinas: tuple[str, ...]
    horario: str
    exige_acompanhante: bool


# ---------------------------------------------------------------------------
# Conversão de texto digitado
# ---------------------------------------------------------------------------
def ler_inteiro(texto: str, campo: str) -> int:
    """Converte texto em inteiro ou levanta ErroDeValidacao."""
    limpo = str(texto).strip()
    try:
        return int(limpo)
    except ValueError:
        raise ErroDeValidacao(
            f"{campo}: digite um número inteiro (você digitou '{limpo}')."
        ) from None


def ler_sim_nao(texto: str) -> bool:
    """Aceita s/sim/n/nao/não em qualquer combinação de maiúsculas."""
    limpo = str(texto).strip().lower()
    if limpo in ("s", "sim"):
        return True
    if limpo in ("n", "nao", "não"):
        return False
    raise ErroDeValidacao("Responda com 's' para sim ou 'n' para não.")


# ---------------------------------------------------------------------------
# Validações (cada uma devolve o valor limpo ou levanta ErroDeValidacao)
# ---------------------------------------------------------------------------
def _exigir_inteiro(valor, campo: str) -> int:
    # bool é subclasse de int em Python; True não pode valer como "1 ano".
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ErroDeValidacao(f"{campo}: precisa ser um número inteiro.")
    return valor


def validar_nome(nome: str) -> str:
    if not isinstance(nome, str):
        raise ErroDeValidacao("Nome: precisa ser um texto.")
    limpo = nome.strip()
    if len(limpo) < 2:
        raise ErroDeValidacao("Nome: informe pelo menos 2 caracteres.")
    if len(limpo) > 80:
        raise ErroDeValidacao("Nome: use no máximo 80 caracteres.")
    return limpo


def validar_idade(idade: int) -> int:
    idade = _exigir_inteiro(idade, "Idade")
    if idade < IDADE_MINIMA:
        raise ErroDeValidacao(
            f"Idade: o clube só aceita sócios a partir de {IDADE_MINIMA} anos."
        )
    if idade > IDADE_MAXIMA:
        raise ErroDeValidacao(f"Idade: o máximo aceito é {IDADE_MAXIMA} anos.")
    return idade


def validar_membros_familia(quantidade: int) -> int:
    quantidade = _exigir_inteiro(quantidade, "Pessoas da família")
    if quantidade < 1:
        raise ErroDeValidacao(
            "Pessoas da família: o mínimo é 1 (o próprio candidato conta)."
        )
    if quantidade > MAX_MEMBROS_FAMILIA:
        raise ErroDeValidacao(
            f"Pessoas da família: o máximo aceito é {MAX_MEMBROS_FAMILIA}."
        )
    return quantidade


def validar_anos_associado(anos: int, idade: int) -> int:
    anos = _exigir_inteiro(anos, "Anos como sócio")
    if anos < 0:
        raise ErroDeValidacao("Anos como sócio: não pode ser negativo.")
    maximo = idade - IDADE_MINIMA
    if anos > maximo:
        raise ErroDeValidacao(
            f"Anos como sócio: com {idade} anos de idade, o máximo possível "
            f"é {maximo} (o clube só aceita sócios a partir de {IDADE_MINIMA} anos)."
        )
    return anos


def validar_modalidade(chave: str, idade: int) -> Modalidade:
    for modalidade in MODALIDADES:
        if modalidade.chave == chave:
            if not modalidade.idade_min <= idade <= modalidade.idade_max:
                raise ErroDeValidacao(
                    f"Modalidade '{modalidade.nome}' é permitida apenas de "
                    f"{modalidade.idade_min} a {modalidade.idade_max} anos."
                )
            return modalidade
    raise ErroDeValidacao(f"Modalidade desconhecida: '{chave}'.")


def modalidades_disponiveis(idade: int) -> tuple[Modalidade, ...]:
    """Modalidades que uma pessoa dessa idade pode escolher."""
    return tuple(m for m in MODALIDADES if m.idade_min <= idade <= m.idade_max)


# ---------------------------------------------------------------------------
# Cálculo
# ---------------------------------------------------------------------------
def descobrir_categoria(idade: int) -> Categoria:
    idade = validar_idade(idade)
    for categoria in CATEGORIAS:
        if categoria.idade_min <= idade <= categoria.idade_max:
            return categoria
    # Só chega aqui se alguém editar CATEGORIAS e deixar uma faixa de idade sem dono
    # (há um teste que protege contra isso).
    raise ErroDeValidacao(f"Nenhuma categoria para a idade {idade}.")


def arredondar(valor: Decimal) -> Decimal:
    """Arredonda para centavos (0,5 centavo sobe)."""
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def percentual_familia(membros: int) -> Decimal:
    if membros >= 3:
        return Decimal("0.15")
    if membros == 2:
        return Decimal("0.10")
    return Decimal("0")


def percentual_tempo_de_socio(anos: int) -> Decimal:
    if anos >= 10:
        return Decimal("0.10")
    if anos >= 5:
        return Decimal("0.05")
    return Decimal("0")


def calcular_adesao(solicitacao: Solicitacao) -> Resultado:
    """Valida a solicitação e calcula categoria, valores e permissões."""
    # Valida tudo de novo: quem chamar esta função direto também fica protegido.
    nome = validar_nome(solicitacao.nome)
    idade = validar_idade(solicitacao.idade)
    modalidade = validar_modalidade(solicitacao.modalidade, idade)
    membros = validar_membros_familia(solicitacao.membros_familia)
    anos = validar_anos_associado(solicitacao.anos_associado, idade)

    categoria = descobrir_categoria(idade)

    # Valor antes dos descontos
    adicional_aquecida = (
        ADICIONAL_PISCINA_AQUECIDA if solicitacao.piscina_aquecida else Decimal("0.00")
    )
    subtotal = categoria.mensalidade + modalidade.adicional + adicional_aquecida

    # Descontos: cada um calculado sobre o subtotal e depois somados
    candidatos = [
        (f"Família, {membros} pessoas", percentual_familia(membros)),
        (f"Tempo de sócio, {anos} anos", percentual_tempo_de_socio(anos)),
        ("Pagamento anual à vista",
         DESCONTO_PAGAMENTO_ANUAL if solicitacao.pagamento_anual else Decimal("0")),
    ]
    descontos = tuple(
        Desconto(descricao, pct, arredondar(subtotal * pct))
        for descricao, pct in candidatos
        if pct > 0
    )

    soma_percentuais = sum((d.percentual for d in descontos), Decimal("0"))
    limite_aplicado = soma_percentuais > LIMITE_DESCONTO
    percentual_aplicado = min(soma_percentuais, LIMITE_DESCONTO)

    desconto_total = arredondar(subtotal * percentual_aplicado)
    total_mensal = subtotal - desconto_total
    total_anual = (
        arredondar(total_mensal * MESES_NO_ANO) if solicitacao.pagamento_anual else None
    )

    # Permissões de uso
    piscinas = categoria.piscinas
    if solicitacao.piscina_aquecida:
        piscinas = piscinas + (PISCINA_AQUECIDA,)
    horario = f"{categoria.hora_abre:02d}h às {categoria.hora_fecha:02d}h"

    return Resultado(
        nome=nome,
        idade=idade,
        categoria=categoria.nome,
        modalidade=modalidade.nome,
        mensalidade_base=categoria.mensalidade,
        adicional_modalidade=modalidade.adicional,
        adicional_aquecida=adicional_aquecida,
        subtotal=subtotal,
        descontos=descontos,
        percentual_aplicado=percentual_aplicado,
        limite_aplicado=limite_aplicado,
        desconto_total=desconto_total,
        total_mensal=total_mensal,
        total_anual=total_anual,
        piscinas=piscinas,
        horario=horario,
        exige_acompanhante=categoria.exige_acompanhante,
    )
