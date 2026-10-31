"""Testes do Clube Aquático.

Como rodar (na pasta do projeto):
    python3 -m unittest discover -s tests -v
"""

import contextlib
import io
import os
import sys
import unittest
from decimal import Decimal
from unittest import mock

# Permite importar os módulos da pasta src/ sem instalar nada.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import main  # noqa: E402
from regras import (  # noqa: E402
    CATEGORIAS,
    ErroDeValidacao,
    IDADE_MAXIMA,
    IDADE_MINIMA,
    Solicitacao,
    arredondar,
    calcular_adesao,
    descobrir_categoria,
    ler_inteiro,
    ler_sim_nao,
    modalidades_disponiveis,
)


def solicitacao(**mudancas) -> Solicitacao:
    """Solicitação válida e simples; cada teste muda só o que quer testar."""
    dados = dict(
        nome="Ana Souza",
        idade=35,
        modalidade="livre",
        piscina_aquecida=False,
        membros_familia=1,
        anos_associado=0,
        pagamento_anual=False,
    )
    dados.update(mudancas)
    return Solicitacao(**dados)


def D(texto: str) -> Decimal:
    return Decimal(texto)


# ---------------------------------------------------------------------------
# Categoria e mensalidade base
# ---------------------------------------------------------------------------
class TestCategoria(unittest.TestCase):
    def test_limites_de_cada_faixa(self):
        esperado = {
            4: "Infantil", 12: "Infantil",
            13: "Juvenil", 17: "Juvenil",
            18: "Adulto", 59: "Adulto",
            60: "Sênior", 110: "Sênior",
        }
        for idade, categoria in esperado.items():
            with self.subTest(idade=idade):
                self.assertEqual(descobrir_categoria(idade).nome, categoria)

    def test_tabela_cobre_todas_as_idades_sem_buraco_nem_sobreposicao(self):
        # Protege contra erro ao editar a tabela CATEGORIAS.
        for idade in range(IDADE_MINIMA, IDADE_MAXIMA + 1):
            donas = [c.nome for c in CATEGORIAS if c.idade_min <= idade <= c.idade_max]
            with self.subTest(idade=idade):
                self.assertEqual(len(donas), 1, f"idade {idade} -> {donas}")

    def test_mensalidade_base_por_categoria(self):
        esperado = {10: "80.00", 15: "100.00", 35: "150.00", 70: "110.00"}
        for idade, valor in esperado.items():
            with self.subTest(idade=idade):
                resultado = calcular_adesao(solicitacao(idade=idade))
                self.assertEqual(resultado.mensalidade_base, D(valor))
                self.assertEqual(resultado.total_mensal, D(valor))

    def test_crianca_valor_minimo_do_clube(self):
        resultado = calcular_adesao(solicitacao(nome="Lia", idade=4))
        self.assertEqual(resultado.categoria, "Infantil")
        self.assertEqual(resultado.total_mensal, D("80.00"))

    def test_idoso_na_idade_maxima(self):
        resultado = calcular_adesao(solicitacao(idade=110))
        self.assertEqual(resultado.categoria, "Sênior")


# ---------------------------------------------------------------------------
# Modalidades e adicionais
# ---------------------------------------------------------------------------
class TestModalidades(unittest.TestCase):
    def test_adicionais(self):
        esperado = {"livre": "150.00", "natacao": "210.00",
                    "hidro": "200.00", "equipe": "240.00"}
        for chave, total in esperado.items():
            with self.subTest(modalidade=chave):
                resultado = calcular_adesao(solicitacao(modalidade=chave))
                self.assertEqual(resultado.total_mensal, D(total))

    def test_piscina_aquecida_soma_25(self):
        resultado = calcular_adesao(solicitacao(piscina_aquecida=True))
        self.assertEqual(resultado.adicional_aquecida, D("25.00"))
        self.assertEqual(resultado.total_mensal, D("175.00"))

    def test_hidroginastica_so_para_maiores_de_18(self):
        with self.assertRaisesRegex(ErroDeValidacao, "18 a 110"):
            calcular_adesao(solicitacao(idade=17, modalidade="hidro"))
        resultado = calcular_adesao(solicitacao(idade=18, modalidade="hidro"))
        self.assertEqual(resultado.modalidade, "Hidroginástica")

    def test_equipe_de_competicao_de_8_a_59(self):
        for idade in (7, 60):
            with self.subTest(idade=idade, esperado="recusa"):
                with self.assertRaises(ErroDeValidacao):
                    calcular_adesao(solicitacao(idade=idade, modalidade="equipe"))
        for idade in (8, 59):
            with self.subTest(idade=idade, esperado="aceita"):
                resultado = calcular_adesao(solicitacao(idade=idade, modalidade="equipe"))
                self.assertEqual(resultado.modalidade, "Equipe de competição")

    def test_lista_de_modalidades_depende_da_idade(self):
        def chaves(idade):
            return [m.chave for m in modalidades_disponiveis(idade)]

        self.assertEqual(chaves(5), ["livre", "natacao"])
        self.assertEqual(chaves(10), ["livre", "natacao", "equipe"])
        self.assertEqual(chaves(30), ["livre", "natacao", "hidro", "equipe"])
        self.assertEqual(chaves(70), ["livre", "natacao", "hidro"])

    def test_modalidade_desconhecida(self):
        with self.assertRaisesRegex(ErroDeValidacao, "desconhecida"):
            calcular_adesao(solicitacao(modalidade="surfe"))


# ---------------------------------------------------------------------------
# Descontos
# ---------------------------------------------------------------------------
class TestDescontos(unittest.TestCase):
    def total(self, **mudancas):
        return calcular_adesao(solicitacao(**mudancas)).total_mensal

    def test_familia(self):
        self.assertEqual(self.total(membros_familia=1), D("150.00"))
        self.assertEqual(self.total(membros_familia=2), D("135.00"))   # -10%
        self.assertEqual(self.total(membros_familia=3), D("127.50"))   # -15%
        self.assertEqual(self.total(membros_familia=20), D("127.50"))  # continua 15%

    def test_tempo_de_socio_nas_bordas(self):
        self.assertEqual(self.total(anos_associado=4), D("150.00"))
        self.assertEqual(self.total(anos_associado=5), D("142.50"))    # -5%
        self.assertEqual(self.total(anos_associado=9), D("142.50"))
        self.assertEqual(self.total(anos_associado=10), D("135.00"))   # -10%

    def test_pagamento_anual(self):
        resultado = calcular_adesao(solicitacao(pagamento_anual=True))
        self.assertEqual(resultado.total_mensal, D("135.00"))
        self.assertEqual(resultado.total_anual, D("1620.00"))

    def test_sem_pagamento_anual_nao_tem_total_anual(self):
        self.assertIsNone(calcular_adesao(solicitacao()).total_anual)

    def test_exatamente_no_teto_nao_conta_como_limite_aplicado(self):
        resultado = calcular_adesao(
            solicitacao(membros_familia=3, anos_associado=10)  # 15% + 10% = 25%
        )
        self.assertEqual(resultado.percentual_aplicado, D("0.25"))
        self.assertFalse(resultado.limite_aplicado)
        self.assertEqual(resultado.total_mensal, D("112.50"))

    def test_acima_do_teto_e_travado_em_25(self):
        resultado = calcular_adesao(
            solicitacao(membros_familia=3, anos_associado=10, pagamento_anual=True)
        )  # 35% somados
        self.assertTrue(resultado.limite_aplicado)
        self.assertEqual(resultado.percentual_aplicado, D("0.25"))
        self.assertEqual(resultado.desconto_total, D("37.50"))
        self.assertEqual(resultado.total_mensal, D("112.50"))

    def test_sem_descontos_lista_vazia(self):
        self.assertEqual(calcular_adesao(solicitacao()).descontos, ())

    def test_desconto_incide_sobre_o_subtotal_com_adicionais(self):
        resultado = calcular_adesao(
            solicitacao(modalidade="natacao", piscina_aquecida=True, membros_familia=2)
        )  # subtotal 235,00 e 10%
        self.assertEqual(resultado.subtotal, D("235.00"))
        self.assertEqual(resultado.desconto_total, D("23.50"))
        self.assertEqual(resultado.total_mensal, D("211.50"))


class TestExemploDaDocumentacao(unittest.TestCase):
    """O exemplo calculado à mão em docs/regras_de_negocio.md."""

    def test_ana_natacao_aquecida_familia_3_seis_anos_anual(self):
        resultado = calcular_adesao(solicitacao(
            modalidade="natacao", piscina_aquecida=True, membros_familia=3,
            anos_associado=6, pagamento_anual=True,
        ))
        self.assertEqual(resultado.subtotal, D("235.00"))
        self.assertTrue(resultado.limite_aplicado)
        self.assertEqual(resultado.desconto_total, D("58.75"))
        self.assertEqual(resultado.total_mensal, D("176.25"))
        self.assertEqual(resultado.total_anual, D("2115.00"))


# ---------------------------------------------------------------------------
# Permissões de uso
# ---------------------------------------------------------------------------
class TestPermissoes(unittest.TestCase):
    def test_infantil_exige_acompanhante_e_horario_reduzido(self):
        r = calcular_adesao(solicitacao(idade=9))
        self.assertTrue(r.exige_acompanhante)
        self.assertEqual(r.horario, "08h às 18h")
        self.assertIn("Piscina infantil", r.piscinas)
        self.assertNotIn("Piscina semiolímpica", r.piscinas)

    def test_juvenil_ate_21h_sem_acompanhante(self):
        r = calcular_adesao(solicitacao(idade=15))
        self.assertFalse(r.exige_acompanhante)
        self.assertEqual(r.horario, "06h às 21h")
        self.assertIn("Piscina semiolímpica", r.piscinas)

    def test_adulto_e_senior_ate_22h(self):
        for idade in (35, 70):
            with self.subTest(idade=idade):
                r = calcular_adesao(solicitacao(idade=idade))
                self.assertEqual(r.horario, "06h às 22h")
                self.assertFalse(r.exige_acompanhante)

    def test_piscina_aquecida_entra_na_lista(self):
        com = calcular_adesao(solicitacao(piscina_aquecida=True))
        sem = calcular_adesao(solicitacao(piscina_aquecida=False))
        self.assertIn("Piscina aquecida", com.piscinas)
        self.assertNotIn("Piscina aquecida", sem.piscinas)


# ---------------------------------------------------------------------------
# Entradas inválidas
# ---------------------------------------------------------------------------
class TestEntradasInvalidas(unittest.TestCase):
    def assertRecusa(self, trecho_da_mensagem, **mudancas):
        with self.assertRaisesRegex(ErroDeValidacao, trecho_da_mensagem):
            calcular_adesao(solicitacao(**mudancas))

    def test_idade_fora_dos_limites(self):
        self.assertRecusa("a partir de 4", idade=3)
        self.assertRecusa("a partir de 4", idade=0)
        self.assertRecusa("a partir de 4", idade=-5)
        self.assertRecusa("máximo aceito é 110", idade=111)

    def test_idade_de_tipo_errado(self):
        for valor in ("35", 35.0, 12.5, None, True):
            with self.subTest(valor=valor):
                self.assertRecusa("Idade", idade=valor)

    def test_nome_invalido(self):
        self.assertRecusa("pelo menos 2", nome="")
        self.assertRecusa("pelo menos 2", nome="   ")
        self.assertRecusa("pelo menos 2", nome="A")
        self.assertRecusa("no máximo 80", nome="A" * 81)
        self.assertRecusa("texto", nome=None)

    def test_nome_ganha_trim_e_aceita_limite(self):
        self.assertEqual(calcular_adesao(solicitacao(nome="  Ana  ")).nome, "Ana")
        self.assertEqual(len(calcular_adesao(solicitacao(nome="A" * 80)).nome), 80)

    def test_familia_fora_dos_limites(self):
        self.assertRecusa("mínimo é 1", membros_familia=0)
        self.assertRecusa("mínimo é 1", membros_familia=-1)
        self.assertRecusa("máximo aceito é 20", membros_familia=21)

    def test_anos_de_socio_invalidos(self):
        self.assertRecusa("negativo", anos_associado=-1)
        self.assertRecusa("máximo possível é 31", idade=35, anos_associado=32)
        self.assertRecusa("inteiro", anos_associado=2.5)

    def test_anos_de_socio_no_limite_e_aceito(self):
        # 35 anos de idade: pode ter sido sócio desde os 4 (31 anos de casa)
        resultado = calcular_adesao(solicitacao(idade=35, anos_associado=31))
        self.assertEqual(resultado.total_mensal, D("135.00"))  # 10% de tempo de sócio

    def test_crianca_de_4_anos_nao_pode_ter_anos_de_socio(self):
        self.assertRecusa("máximo possível é 0", idade=4, anos_associado=1)


class TestConversoresDeTexto(unittest.TestCase):
    def test_ler_inteiro_aceita_espacos(self):
        self.assertEqual(ler_inteiro("  7 ", "Campo"), 7)
        self.assertEqual(ler_inteiro("-3", "Campo"), -3)

    def test_ler_inteiro_recusa_lixo(self):
        for texto in ("abc", "", "   ", "12.5", "12,5", "1 2", "dez"):
            with self.subTest(texto=texto):
                with self.assertRaises(ErroDeValidacao):
                    ler_inteiro(texto, "Campo")

    def test_ler_sim_nao(self):
        for texto in ("s", "S", "sim", "SIM", " Sim "):
            self.assertTrue(ler_sim_nao(texto), texto)
        for texto in ("n", "N", "nao", "não", "NÃO"):
            self.assertFalse(ler_sim_nao(texto), texto)
        for texto in ("", "talvez", "y", "1"):
            with self.subTest(texto=texto):
                with self.assertRaises(ErroDeValidacao):
                    ler_sim_nao(texto)


# ---------------------------------------------------------------------------
# Dinheiro
# ---------------------------------------------------------------------------
class TestDinheiro(unittest.TestCase):
    def test_arredondamento_meio_centavo_sobe(self):
        # Com as tabelas atuais nenhuma conta gera fração de centavo,
        # então a função é testada direto.
        self.assertEqual(arredondar(D("2.675")), D("2.68"))
        self.assertEqual(arredondar(D("0.005")), D("0.01"))
        self.assertEqual(arredondar(D("0.004")), D("0.00"))

    def test_valores_sao_decimal_e_nao_float(self):
        r = calcular_adesao(solicitacao(
            modalidade="natacao", piscina_aquecida=True,
            membros_familia=3, pagamento_anual=True,
        ))
        for valor in (r.mensalidade_base, r.subtotal, r.desconto_total,
                      r.total_mensal, r.total_anual):
            self.assertIsInstance(valor, Decimal)

    def test_formatacao_em_reais(self):
        self.assertEqual(main.formatar_moeda(D("0")), "R$ 0,00")
        self.assertEqual(main.formatar_moeda(D("80")), "R$ 80,00")
        self.assertEqual(main.formatar_moeda(D("1234.5")), "R$ 1.234,50")
        self.assertEqual(main.formatar_moeda(D("1234567.89")), "R$ 1.234.567,89")


# ---------------------------------------------------------------------------
# Interface de terminal (do começo ao fim, com respostas simuladas)
# ---------------------------------------------------------------------------
class TestInterfaceDeTerminal(unittest.TestCase):
    def executar(self, respostas):
        saida = io.StringIO()
        with mock.patch("builtins.input", side_effect=respostas):
            with contextlib.redirect_stdout(saida):
                main.main()
        return saida.getvalue()

    def test_fluxo_completo_da_ana(self):
        texto = self.executar(
            ["Ana Souza", "35", "2", "s", "3", "6", "s", "n"]
        )
        self.assertIn("Adulto", texto)
        self.assertIn("R$ 176,25", texto)
        self.assertIn("R$ 2.115,00", texto)
        self.assertIn("Limite de 25% de desconto aplicado", texto)
        self.assertIn("Encerrado", texto)

    def test_repete_a_pergunta_quando_a_resposta_e_invalida(self):
        texto = self.executar([
            "", "Ana",             # nome vazio, depois válido
            "3", "200", "abc", "35",  # idade: baixa, alta, texto, válida
            "9", "1",              # modalidade: fora da lista, depois "uso livre"
            "talvez", "n",         # aquecida: inválida, depois não
            "0", "1",              # família: 0 recusado, depois 1
            "-2", "0",             # anos: negativo recusado, depois 0
            "n",                   # pagamento anual
            "n",                   # cadastrar outro? não
        ])
        for trecho in ("pelo menos 2", "a partir de 4 anos", "máximo aceito é 110",
                       "digite um número inteiro", "Escolha um número de 1 a 4",
                       "Responda com 's'", "mínimo é 1", "não pode ser negativo"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, texto)
        self.assertIn("TOTAL MENSAL", texto)
        self.assertIn("R$ 150,00", texto)

    def test_cadastra_dois_socios_na_mesma_execucao(self):
        texto = self.executar([
            "Ana", "35", "1", "n", "1", "0", "n", "s",
            "Lia", "6", "1", "n", "1", "0", "n", "n",
        ])
        self.assertEqual(texto.count("FICHA DO SÓCIO"), 2)
        self.assertIn("Infantil", texto)
        self.assertIn("obrigatório", texto)

    def test_menu_nao_oferece_modalidade_proibida_para_a_idade(self):
        texto = self.executar(
            ["Lia", "6", "1", "n", "1", "0", "n", "n"]
        )
        menu = texto.split("Modalidades disponíveis:")[1].split("Escolha a modalidade")[0]
        self.assertIn("Aulas de natação", menu)
        self.assertNotIn("Hidroginástica", menu)  # só a partir de 18 anos
        self.assertNotIn("Equipe", menu)          # só a partir de 8 anos

    def test_nome_comprido_nao_estoura_a_largura_da_ficha(self):
        nome = "Maria Aparecida de Albuquerque Cavalcanti Nogueira da Silva Santos Pereira"
        texto = self.executar([nome, "70", "3", "s", "3", "12", "s", "n"])
        self.assertIn("Pereira", texto)
        for linha in texto.splitlines():
            self.assertLessEqual(len(linha), main.LARGURA, linha)

    def test_fim_da_entrada_encerra_sem_erro(self):
        texto = self.executar(EOFError())
        self.assertIn("Encerrado", texto)


if __name__ == "__main__":
    unittest.main()
