from fastapi import APIRouter, HTTPException, status
from app.schemas.ai import SearchPlanRequest, SearchPlanResponse
from app.services.ai_planner import AIPlannerService

router = APIRouter(prefix="/ai", tags=["AI Search Planner"])


@router.post("/search-plan", response_model=SearchPlanResponse)
async def create_search_plan(payload: SearchPlanRequest):
    """
    Step 1 of AI Search UX Workflow:
    Parses natural language prompt into a structured SearchPlanResponse.
    The user can review and edit this plan in the UI BEFORE launching a job.
    """
    try:
        plan = await AIPlannerService.analyze_prompt(payload.prompt)
        return plan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to analyze search prompt: {str(e)}",
        )
