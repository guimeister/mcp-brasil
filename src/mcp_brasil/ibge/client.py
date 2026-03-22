"""HTTP client for the IBGE API.

Ported from mcp-dadosbr/lib/tools/government.ts (executeIBGE function).
Extended with nomes and agregados endpoints.

Endpoints:
    - /v1/localidades/estados           → listar_estados
    - /v1/localidades/estados/{uf}/municipios → listar_municipios
    - /v1/localidades/regioes           → listar_regioes
    - /v2/censos/nomes/{nome}           → consultar_nome
    - /v2/censos/nomes/ranking          → ranking_nomes
    - /v3/agregados/{id}/periodos/...   → consultar_agregado
"""

from __future__ import annotations

from typing import Any

from mcp_brasil._shared.http_client import http_get

from .constants import AGREGADOS_URL, LOCALIDADES_URL, NIVEIS_TERRITORIAIS, NOMES_URL
from .schemas import AgregadoValor, Estado, Municipio, NomeConsulta, RankingResult, Regiao


async def listar_estados() -> list[Estado]:
    """Fetch all 27 Brazilian states ordered by name.

    Ref: mcp-dadosbr executeIBGE("estados")
    """
    data = await http_get(f"{LOCALIDADES_URL}/estados", params={"orderBy": "nome"})
    return [
        Estado(
            id=e["id"],
            sigla=e["sigla"],
            nome=e["nome"],
            regiao=Regiao(**e["regiao"]),
        )
        for e in data
    ]


async def listar_municipios(uf: str) -> list[Municipio]:
    """Fetch municipalities for a given state.

    Ref: mcp-dadosbr executeIBGE("municipios_por_uf")

    Args:
        uf: 2-letter state code (e.g. "SP", "PI").
    """
    data = await http_get(
        f"{LOCALIDADES_URL}/estados/{uf.upper()}/municipios",
        params={"orderBy": "nome"},
    )
    return [Municipio(id=m["id"], nome=m["nome"]) for m in data]


async def listar_regioes() -> list[Regiao]:
    """Fetch the 5 Brazilian macro-regions.

    Ref: mcp-dadosbr executeIBGE("regioes")
    """
    data = await http_get(f"{LOCALIDADES_URL}/regioes")
    return [Regiao(**r) for r in data]


async def consultar_nome(nome: str) -> list[NomeConsulta]:
    """Fetch frequency over decades for a given name.

    API: GET /v2/censos/nomes/{nome}

    Args:
        nome: Name to query (e.g. "João").
    """
    data = await http_get(f"{NOMES_URL}/{nome}")
    return [NomeConsulta(**item) for item in data]


async def ranking_nomes(
    localidade: str | None = None,
    sexo: str | None = None,
) -> list[RankingResult]:
    """Fetch name ranking (top names in Brazil or in a locality).

    API: GET /v2/censos/nomes/ranking

    Args:
        localidade: IBGE code of state/municipality (optional).
        sexo: "M" or "F" to filter by gender (optional).
    """
    params: dict[str, str] = {}
    if localidade:
        params["localidade"] = localidade
    if sexo:
        params["sexo"] = sexo.upper()

    data = await http_get(f"{NOMES_URL}/ranking", params=params or None)
    return [RankingResult(**item) for item in data]


async def consultar_agregado(
    agregado_id: int,
    variavel_id: int,
    nivel: str = "estado",
    localidade: str = "all",
    periodos: str = "-6",
) -> list[AgregadoValor]:
    """Fetch aggregated data from IBGE (population, GDP, etc).

    API: GET /v3/agregados/{id}/periodos/{periodos}/variaveis/{variavel}

    Args:
        agregado_id: Aggregate research ID.
        variavel_id: Variable ID within the aggregate.
        nivel: Territorial level (pais, regiao, estado, municipio).
        localidade: Locality code or "all".
        periodos: Period spec (e.g. "-6" for last 6, "2020|2021", etc).
    """
    nivel_codigo = NIVEIS_TERRITORIAIS.get(nivel, "N3")
    localidades_param = f"{nivel_codigo}[{localidade}]"

    url = f"{AGREGADOS_URL}/{agregado_id}/periodos/{periodos}/variaveis/{variavel_id}"
    params = {"localidades": localidades_param}

    data: list[dict[str, Any]] = await http_get(url, params=params)

    resultados: list[AgregadoValor] = []
    for variavel in data:
        for resultado in variavel.get("resultados", []):
            for serie in resultado.get("series", []):
                loc = serie.get("localidade", {})
                for _periodo, valor in serie.get("serie", {}).items():
                    resultados.append(
                        AgregadoValor(
                            localidade_id=str(loc.get("id", "")),
                            localidade_nome=loc.get("nome", ""),
                            valor=valor,
                        )
                    )

    return resultados


async def listar_pesquisas() -> list[dict[str, Any]]:
    """Fetch list of available IBGE research/aggregates.

    API: GET /v3/agregados
    Returns top-level research IDs with their aggregate sub-IDs.
    """
    data: list[dict[str, Any]] = await http_get(AGREGADOS_URL)
    return data
