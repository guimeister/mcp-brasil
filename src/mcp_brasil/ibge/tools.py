"""Tool functions for IBGE feature.

Ported from mcp-dadosbr/lib/tools/government.ts executeIBGE().
Extended with nomes, agregados, and pesquisas tools.

Rules (ADR-001):
    - tools.py NEVER makes HTTP directly — delegates to client.py
    - Returns formatted strings for LLM consumption
"""

from __future__ import annotations

from mcp_brasil._shared.formatting import markdown_table, truncate_list

from . import client
from .constants import AGREGADOS_POPULARES


async def listar_estados() -> str:
    """Lista todos os 27 estados brasileiros com sigla, nome e região.

    Consulta dados geográficos do IBGE.
    Útil para obter siglas de UF, nomes de estados e suas regiões.

    Returns:
        Tabela com todos os estados brasileiros.
    """
    estados = await client.listar_estados()
    rows = [(e.sigla, e.nome, e.regiao.nome) for e in estados]
    return markdown_table(["UF", "Nome", "Região"], rows)


async def buscar_municipios(uf: str) -> str:
    """Busca todos os municípios de um estado pela sigla da UF.

    Retorna a lista de municípios com código IBGE e nome.
    O Brasil tem ~5.570 municípios distribuídos em 27 UFs.

    Args:
        uf: Sigla do estado com 2 letras (ex: SP, RJ, PI, BA).

    Returns:
        Lista de municípios do estado.
    """
    municipios = await client.listar_municipios(uf)
    items = [f"{m.id} — {m.nome}" for m in municipios]
    header = f"Municípios de {uf.upper()} ({len(municipios)} encontrados):\n\n"
    return header + truncate_list(items, max_items=100)


async def listar_regioes() -> str:
    """Lista as 5 macro-regiões do Brasil.

    Regiões: Norte, Nordeste, Centro-Oeste, Sudeste, Sul.

    Returns:
        Tabela com as regiões brasileiras.
    """
    regioes = await client.listar_regioes()
    rows = [(r.sigla, r.nome) for r in regioes]
    return markdown_table(["Sigla", "Região"], rows)


async def consultar_nome(nome: str) -> str:
    """Consulta a frequência de um nome ao longo das décadas no Brasil.

    Dados do Censo Demográfico do IBGE. Mostra quantas pessoas
    foram registradas com esse nome em cada período de 10 anos
    (de 1930 até 2010).

    Args:
        nome: Nome a consultar (ex: João, Maria, Pedro).

    Returns:
        Evolução da frequência do nome por década.
    """
    resultados = await client.consultar_nome(nome)
    if not resultados:
        return f"Nome '{nome}' não encontrado nos dados do IBGE."

    lines: list[str] = []
    for item in resultados:
        lines.append(f"Nome: {item.nome}")
        if item.sexo:
            lines.append(f"Sexo: {item.sexo}")
        rows = [(r.periodo, f"{r.frequencia:,}".replace(",", ".")) for r in item.res]
        lines.append(markdown_table(["Período", "Frequência"], rows))
        lines.append("")

    return "\n".join(lines)


async def ranking_nomes(localidade: str | None = None, sexo: str | None = None) -> str:
    """Mostra o ranking dos nomes mais populares do Brasil.

    Dados do Censo Demográfico do IBGE. Pode filtrar por estado
    ou município (usando o código IBGE) e por sexo.

    Args:
        localidade: Código IBGE do estado ou município (opcional).
                    Ex: "33" para RJ, "3550308" para São Paulo capital.
        sexo: Filtrar por sexo: "M" para masculino, "F" para feminino (opcional).

    Returns:
        Ranking dos nomes mais frequentes.
    """
    resultados = await client.ranking_nomes(localidade=localidade, sexo=sexo)
    if not resultados:
        return "Nenhum resultado encontrado para o ranking de nomes."

    lines: list[str] = []
    for item in resultados:
        rows = [(str(r.ranking), r.nome, f"{r.frequencia:,}".replace(",", ".")) for r in item.res]
        lines.append(markdown_table(["#", "Nome", "Frequência"], rows))

    return "\n".join(lines)


async def consultar_agregado(
    indicador: str = "",
    agregado_id: int = 0,
    variavel_id: int = 0,
    nivel: str = "estado",
    localidade: str = "all",
    periodos: str = "-6",
) -> str:
    """Consulta dados agregados de pesquisas do IBGE.

    Permite acessar indicadores como população, PIB, PIB per capita,
    e área territorial por estado, município ou região.

    Para indicadores comuns, use o parâmetro 'indicador':
    - "populacao": População residente estimada
    - "pib": Produto Interno Bruto
    - "pib_per_capita": PIB per capita
    - "area_territorial": Área territorial em km²

    Para outros agregados, informe agregado_id e variavel_id diretamente.
    Use a tool listar_pesquisas() para descobrir IDs disponíveis.

    Args:
        indicador: Atalho para indicadores comuns
            (populacao, pib, pib_per_capita, area_territorial).
        agregado_id: ID do agregado IBGE (usado se indicador não informado).
        variavel_id: ID da variável dentro do agregado.
        nivel: Nível territorial: pais, regiao, estado, municipio.
        localidade: Código IBGE ou "all" para todas.
        periodos: Períodos a consultar ("-6" para últimos 6, "2020|2021", etc).

    Returns:
        Tabela com os dados do agregado.
    """
    if indicador and indicador in AGREGADOS_POPULARES:
        info = AGREGADOS_POPULARES[indicador]
        agregado_id = int(info["id"])
        variavel_id = int(info["variavel"])

    if not agregado_id or not variavel_id:
        indicadores_disponiveis = ", ".join(AGREGADOS_POPULARES.keys())
        return f"Informe 'indicador' ({indicadores_disponiveis}) ou 'agregado_id' + 'variavel_id'."

    resultados = await client.consultar_agregado(
        agregado_id=agregado_id,
        variavel_id=variavel_id,
        nivel=nivel,
        localidade=localidade,
        periodos=periodos,
    )

    if not resultados:
        return "Nenhum dado encontrado para os parâmetros informados."

    rows = [(r.localidade_nome, r.valor or "—") for r in resultados]
    titulo = ""
    if indicador and indicador in AGREGADOS_POPULARES:
        titulo = f"{AGREGADOS_POPULARES[indicador]['descricao']}\n\n"

    return titulo + markdown_table(["Localidade", "Valor"], rows)


async def listar_pesquisas() -> str:
    """Lista as pesquisas e agregados disponíveis no IBGE.

    Retorna os IDs de pesquisa e agregados que podem ser usados
    com a tool consultar_agregado(). Útil para descobrir quais
    dados estatísticos estão disponíveis.

    Returns:
        Lista de pesquisas com seus agregados.
    """
    pesquisas = await client.listar_pesquisas()
    if not pesquisas:
        return "Nenhuma pesquisa encontrada."

    lines: list[str] = []
    for p in pesquisas[:30]:
        lines.append(f"**{p.get('id', '')}** — {p.get('nome', '')}")
        for ag in p.get("agregados", [])[:3]:
            lines.append(f"  - Agregado {ag.get('id', '')}: {ag.get('nome', '')}")

    if len(pesquisas) > 30:
        lines.append(f"\n... e mais {len(pesquisas) - 30} pesquisas.")

    return "\n".join(lines)
