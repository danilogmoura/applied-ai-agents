"""
Embeddings via API MaaS da Qwen (compatível com OpenAI).

O endpoint `https://maas.qwencloudapi.com/compatible-mode/v1` expõe a mesma
superfície do SDK `openai`, então usamos `OpenAI(base_url=..., api_key=...)`
e trocamos só o nome do modelo. Nada aqui depende de chave OpenAI.

Requisitos (lidos de .env via shared.security):
    - QWEN_MAAS_API_KEY   : chave de acesso ao MaaS
    - EMBEDDING_MODEL     : opcional; default "openai/qwen3.7-text-embedding"

Custo: embeddar ~6.5k chunks uma única vez. Expomos `estimate_embed_cost()`
para você aprovar ANTES de chamar a API — nada é enviado sem cotação explícita.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIGURAÇÃO QWEN MaaS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

QWEN_API_BASE = "https://maas.qwencloudapi.com/compatible-mode/v1"
# Nome REAL aceito pelo endpoint MaaS (validado via smoke test). O prefixo
# "openai/" é sintaxe do LiteLLM proxy e NÃO funciona chamando a API direto.
DEFAULT_EMBED_MODEL = "qwen3.7-text-embedding"
# Modelo multilíngue (Tongyi/Qwen3.7). Suporta dimensão customizada 256..2560;
# default retornado pela API quando não pedimos = 1024 (validado via curl).
# DECISÃO: fixamos 1024 para este corpus (~6.5k chunks). Armazenamento no ChromaDB
# é irrisório (~26 MB float32), então não compensa reduzir dim p/ economizar; e
# dimensões maiores (>1024) dão ganho marginal de recall com mais latência de busca.
# Ajuste via env EMBEDDING_DIMENSION se quiser trocar o trade-off.
EMBED_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1024"))
DIM_RANGE = (256, 2560)

# Mantido por compatibilidade com imports antigos (build_index/query).
EMBED_MODEL = DEFAULT_EMBED_MODEL

# Preço por 1M de tokens de input — ficha oficial qwen3.7-text-embedding: US$0.07/M.
# Sobrescreva via env EMBED_PRICE_PER_1M se o plano tiver outra tabela.
PRICE_PER_1M_INPUT_TOKENS = float(os.getenv("EMBED_PRICE_PER_1M", "0.07"))  # USD

_BATCH_SIZE = 10  # alguns gateways limitam N por request; 10 é conservador.


def resolve_model() -> str:
    """Nome do modelo de embedding: env EMBEDDING_MODEL ou default.

    Normaliza o prefixo "openai/" (usado em config LiteLLM) para o nome real
    que o endpoint MaaS aceita quando chamamos a API diretamente.
    """
    name = os.getenv("EMBEDDING_MODEL", DEFAULT_EMBED_MODEL)
    if name.startswith("openai/"):
        name = name.split("/", 1)[1]
    return name


@dataclass
class EmbedCost:
    """Cotação de um job de embeddings."""

    n_chunks: int
    total_tokens: int
    usd: float

    def __str__(self) -> str:
        return (
            f"{self.n_chunks} chunks · {self.total_tokens:,} tokens · "
            f"US$ {self.usd:.4f} ({resolve_model()})"
        )


def estimate_embed_cost(total_tokens: int, n_chunks: int) -> EmbedCost:
    """Estima o custo de embeddar `total_tokens` no modelo configurado."""
    usd = (total_tokens / 1_000_000) * PRICE_PER_1M_INPUT_TOKENS
    return EmbedCost(n_chunks=n_chunks, total_tokens=total_tokens, usd=usd)


class QwenEmbedder:
    """Wrapper fino sobre o client de embeddings (Qwen MaaS), com batching."""

    def __init__(self, model: str | None = None, dimensions: int | None = None) -> None:
        # Valida dimensão ANTES de qualquer import/chave: falha local e clara.
        if dimensions is not None and not (DIM_RANGE[0] <= dimensions <= DIM_RANGE[1]):
            raise ValueError(
                f"dimensions={dimensions} fora da faixa {DIM_RANGE} aceita pelo modelo"
            )

        from openai import OpenAI  # import tardio: só exige a lib ao usar

        from shared.security import get_required_secret

        api_key = get_required_secret("QWEN_MAAS_API_KEY")
        self.client = OpenAI(api_key=api_key, base_url=QWEN_API_BASE)
        self.model = model or resolve_model()
        # Dimensão customizada (256..2560). None => usa default do gateway (1024).
        self.dimensions = dimensions

    def embed(self, texts: list[str], batch_size: int = _BATCH_SIZE) -> list[list[float]]:
        """Retorna um vetor por texto, na mesma ordem de entrada."""
        vectors: list[list[float]] = []
        kwargs: dict = {"model": self.model}
        if self.dimensions is not None:
            kwargs["dimensions"] = self.dimensions
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            resp = self.client.embeddings.create(input=batch, **kwargs)
            # Garante ordem: alguns gateways reordenam; ordenamos por index.
            ordered = sorted(resp.data, key=lambda d: d.index)
            vectors.extend(item.embedding for item in ordered)
        return vectors

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]


# Compatibilidade retroativa: build_index.py e query.py usam este nome.
OpenAIEmbedder = QwenEmbedder
