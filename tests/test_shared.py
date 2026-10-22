"""Testes unitários para os utilitários compartilhados."""

import pytest
from unittest.mock import patch, MagicMock


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTES DE CUSTO (shared/cost.py)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestCostEstimation:
    """Testes para estimativa de custos."""
    
    def test_count_tokens_simple_text(self):
        """Conta tokens em texto simples."""
        from shared.cost import count_tokens
        
        text = "Olá mundo!"
        tokens = count_tokens(text, model="gpt-4o-mini")
        
        assert tokens > 0
        assert isinstance(tokens, int)
    
    def test_estimate_cost_gpt4o_mini(self):
        """Calcula custo para gpt-4o-mini."""
        from shared.cost import estimate_cost
        
        cost = estimate_cost(100, 50, model="gpt-4o-mini")
        
        assert cost >= 0
        # gpt-4o-mini: $0.15/M input, $0.60/M output
        expected = (100 * 0.15 + 50 * 0.60) / 1_000_000
        assert abs(cost - expected) < 0.000001
    
    def test_format_cost_small(self):
        """Formata custos muito pequenos."""
        from shared.cost import format_cost
        
        assert format_cost(0.0000001) == "$0.00000010"
        assert format_cost(0.001) == "$0.0010"
        assert format_cost(1.23456) == "$1.2346"
    
    def test_summarize_usage(self):
        """Gera resumo completo de uso."""
        from shared.cost import summarize_usage
        
        usage = summarize_usage(500, 200, model="gpt-4o-mini")
        
        assert usage["model"] == "gpt-4o-mini"
        assert usage["input_tokens"] == 500
        assert usage["output_tokens"] == 200
        assert usage["total_tokens"] == 700
        assert "cost_usd" in usage


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTES DE SEGURANÇA (shared/security.py)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestSecurity:
    """Testes para gestão de secrets."""
    
    def test_mask_secret(self):
        """Mascara secret corretamente."""
        from shared.security import mask_secret
        
        masked = mask_secret("sk-1234567890abcdef", visible_chars=4)
        
        assert "****" in masked
        assert len(masked) < len("sk-1234567890abcdef")
    
    def test_mask_secret_short(self):
        """Secret curta é totalmente mascarada."""
        from shared.security import mask_secret
        
        assert mask_secret("abc") == "****"
    
    def test_sanitize_for_log(self):
        """Sanitiza chaves em logs."""
        from shared.security import sanitize_for_log
        
        text = "Usando sk-1234567890abcdef para autenticação"
        sanitized = sanitize_for_log(text)
        
        assert "sk-****" in sanitized
        assert "1234567890abcdef" not in sanitized


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTES DE GOVERNANÇA (shared/governance.py)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestGovernance:
    """Testes para governança e HITL."""
    
    def test_risk_level_enum(self):
        """Enum de níveis de risco."""
        from shared.governance import RiskLevel
        
        levels = [e.value for e in RiskLevel]
        assert "low" in levels
        assert "critical" in levels
    
    def test_action_request_dataclass(self):
        """Criação de solicitação de ação."""
        from shared.governance import ActionRequest, RiskLevel
        
        action = ActionRequest(
            operation="test_op",
            target="test_target",
            reason="test_reason",
            risk_level=RiskLevel.LOW,
        )
        
        assert action.operation == "test_op"
        assert action.risk_level == RiskLevel.LOW


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTES DE LOGGING (shared/logging_config.py)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestLogging:
    """Testes para logging estruturado."""
    
    def test_setup_logging(self):
        """Configura logger."""
        from shared.logging_config import setup_logging
        
        logger = setup_logging("test_module")
        
        assert logger.name == "test_module"
        assert hasattr(logger, "info")
    
    def test_measure_latency_context_manager(self):
        """Mede latência com context manager."""
        from shared.logging_config import measure_latency, setup_logging
        
        logger = setup_logging("test_latency")
        
        with measure_latency(logger, "test_op") as metrics:
            import time
            time.sleep(0.01)  # 10ms
        
        assert "latency_ms" in metrics
        assert metrics["latency_ms"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
