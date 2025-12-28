from fastapi import APIRouter, HTTPException, status
from services.auth import tokenInterceptor
from modules.scheduler import _scheduler_service


router = APIRouter()


@router.get("/list")
async def test():
    return _scheduler_service.list_jobs()


@router.post("/run")
async def run_task(job_id: str):
    try:
        await _scheduler_service.run_job(job_id)
        return {"message": f"Job '{job_id}' executed successfully"}

    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
