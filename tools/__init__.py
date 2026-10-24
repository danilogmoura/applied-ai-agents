"""
Ferramentas offline de validação de corpus.

Pipeline que transforma os livros/documentos em `docs/applied-ai-agents/`
num índice vetorial pesquisável — SEM carregar o texto integral no LLM.

Etapas:
    1. extract   — lê .epub (ZIP/XHTML) e .md, devolve blocos de texto + fonte
    2. chunk     — divide em pedaços com sobreposição e metadados de citação
    3. embed     — gera vetores via OpenAI text-embedding-3-small
    4. index     — grava em ChromaDB persistente para busca posterior

Uso rápido (CLI):
    python -m tools.build_index          # constrói/atualiza o índice
    python -m tools.query "planejamento resiliente"   # testa a recuperação
"""
