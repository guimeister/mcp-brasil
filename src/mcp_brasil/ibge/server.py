"""IBGE feature server — registers tools on a FastMCP instance.

This file only registers tools. Zero business logic (ADR-001 rule #4).
"""

from fastmcp import FastMCP

from .tools import (
    buscar_municipios,
    consultar_agregado,
    consultar_nome,
    listar_estados,
    listar_pesquisas,
    listar_regioes,
    ranking_nomes,
)

mcp = FastMCP("mcp-brasil-ibge")

mcp.tool(listar_estados)
mcp.tool(buscar_municipios)
mcp.tool(listar_regioes)
mcp.tool(consultar_nome)
mcp.tool(ranking_nomes)
mcp.tool(consultar_agregado)
mcp.tool(listar_pesquisas)
