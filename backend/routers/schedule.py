from fastapi import APIRouter, HTTPException, status
from services.auth import tokenInterceptor
from services.schedule import *


router = APIRouter()


@router.get("/list")
async def list_jobs():
    return list_jobs_service()


@router.post("/run")
async def run_task(job_id: str):
    try:
        await run_job_service(job_id)
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
