from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.core.ai_provider import BaseAIProvider, LocalAIProvider
from app.core.providers.gemini_provider import GeminiAIProvider
from app.schemas.ai import SearchPlanResponse
from app.core.config import settings
from app.core.logging import logger


class AIProviderManager:
    """
    Multi-Provider AI Architecture Manager.
    Handles task routing (Search Planning, Research, Email Generation),
    cost policy control (free_only vs free_first), health checks, and fallback logic.
    Primary AI Provider: Google Gemini. Fallback: OpenAI / Rule Parser.
    """

    def __init__(self):
        self.gemini = GeminiAIProvider()
        self.local_fallback = LocalAIProvider()

    def get_active_provider_info(self) -> Dict[str, Any]:
        return {
            "gemini_configured": self.gemini.credentials_present,
            "gemini_model": settings.GEMINI_MODEL,
            "openai_configured": bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip()),
            "openai_model": settings.OPENAI_MODEL,
            "ai_cost_mode": settings.AI_COST_MODE,
        }


    async def analyze_prompt(self, prompt: str) -> Optional[SearchPlanResponse]:
        # 1. Primary Route: Gemini API
        if self.gemini.credentials_present:
            try:
                res = await self.gemini.analyze_prompt(prompt)
                if res:
                    return res
            except Exception as e:
                logger.warning(f"Gemini AI prompt analysis failed: {e}")

        # 2. Fallback: OpenAI if configured and allowed by cost policy
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip():
            if settings.AI_COST_MODE == "free_first" or settings.ENVIRONMENT == "development":
                try:
                    from app.services.ai_planner import AIPlannerService
                    return await AIPlannerService._call_llm(prompt)
                except Exception as e:
                    logger.warning(f"OpenAI fallback prompt analysis failed: {e}")

        # 3. Final Fallback: Rule-Based Deterministic Parser (Zero API Cost, Rule-Grounded)
        from app.services.ai_planner import AIPlannerService
        return AIPlannerService._parse_rule_based(prompt, prompt.lower().strip())

    def get_ai_provider_health(self) -> List[Dict[str, Any]]:
        now_str = datetime.now(timezone.utc).isoformat()
        
        gemini_creds = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip())
        openai_creds = bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip())

        return [
            {
                "name": "Gemini",
                "status": "Connected" if gemini_creds else "Not Configured",
                "enabled": gemini_creds,
                "credentials_present": gemini_creds,
                "model": settings.GEMINI_MODEL,
                "last_checked": now_str,
                "error": "" if gemini_creds else "GEMINI_API_KEY not configured in environment.",
            },
            {
                "name": "OpenAI",
                "status": "Connected" if openai_creds else "Not Configured",
                "enabled": openai_creds,
                "credentials_present": openai_creds,
                "model": settings.OPENAI_MODEL,
                "last_checked": now_str,
                "error": "" if openai_creds else "OPENAI_API_KEY not configured in environment.",
            },
        ]


ai_provider_manager = AIProviderManager()
