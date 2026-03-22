"""Pydantic models for IBGE API responses."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Regiao(BaseModel):
    """Macro-região brasileira."""

    id: int
    sigla: str
    nome: str


class Estado(BaseModel):
    """Estado brasileiro."""

    id: int
    sigla: str
    nome: str
    regiao: Regiao


class Municipio(BaseModel):
    """Município brasileiro (formato simplificado)."""

    id: int = Field(description="Código IBGE de 7 dígitos")
    nome: str


class NomeFrequencia(BaseModel):
    """Frequência de um nome em um período (endpoint /nomes/{nome})."""

    periodo: str
    frequencia: int


class NomeConsulta(BaseModel):
    """Resultado de consulta de frequência de um nome por década."""

    nome: str
    sexo: str | None = None
    localidade: str
    res: list[NomeFrequencia]


class RankingEntry(BaseModel):
    """Uma entrada no ranking de nomes (endpoint /nomes/ranking)."""

    nome: str
    frequencia: int
    ranking: int


class RankingResult(BaseModel):
    """Resultado do ranking de nomes."""

    localidade: str
    sexo: str | None = None
    res: list[RankingEntry]


class AgregadoValor(BaseModel):
    """Valor de uma variável de agregado IBGE."""

    localidade_id: str
    localidade_nome: str
    valor: str | None = None
