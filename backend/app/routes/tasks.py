"""Task status endpoints for async operations."""
from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from ..workers import celery
from ..schemas.prediction import TaskStatusResponse

router = APIRouter()


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Get status of an async task.
    """
    try:
        task_result = AsyncResult(task_id, app=celery)
        
        if task_result.state == 'PENDING':
            response = {
                'task_id': task_id,
                'status': 'pending',
                'result': None,
                'error': None
            }
        elif task_result.state == 'PROGRESS':
            response = {
                'task_id': task_id,
                'status': 'in_progress',
                'result': task_result.info,
                'error': None
            }
        elif task_result.state == 'SUCCESS':
            response = {
                'task_id': task_id,
                'status': 'success',
                'result': task_result.result,
                'error': None
            }
        else:  # FAILURE or other states
            response = {
                'task_id': task_id,
                'status': task_result.state.lower(),
                'result': None,
                'error': str(task_result.info) if task_result.info else 'Task failed'
            }
        
        return TaskStatusResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")

