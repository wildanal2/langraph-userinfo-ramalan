from fastapi import APIRouter, BackgroundTasks, HTTPException
from src.rag.ingestion.ingestion_pipeline import ingestion_pipeline
from src.models.schemas import IngestRequest
from src.rag.utils.collection_handler import get_active_collection
from src.models.schemas import IngestStatusResponse

router = APIRouter(tags=["ingest"])

ingestion_status = {
    "status": "idle",
    "message": "No ingestion running",
    "result": None
}

async def ingestion_task(**kwargs):
    try:
        ingestion_status["status"] = "in_progress"
        ingestion_status["message"] = "Ingestion on progress..."        
        result = await ingestion_pipeline(**kwargs)
        ingestion_status.update({
            "status": "completed",
            "message": "Ingestion completed successfully",
            "result": result
        })
    except Exception as e:
        ingestion_status.update({
            "status": "failed",
            "message": "Ingestion failed",
            "result": str(e)
        })

@router.post("/ingest")
async def ingest(request: IngestRequest, background: BackgroundTasks):
    if ingestion_status["status"] == "in_progress":
        raise HTTPException(
            status_code=409, 
            detail="Ingestion process in progress..."
        )
    background.add_task(
        ingestion_task,
        s3_bucket=request.s3_bucket,
        s3_prefix=request.s3_prefix,
        PARENT_CHUNK_SIZE=request.parent_chunk_size,
        PARENT_CHUNK_OVERLAP=request.parent_chunk_overlap,
        CHILD_CHUNK_SIZE=request.child_chunk_size,
        CHILD_CHUNK_OVERLAP=request.child_chunk_overlap
    )
    return {
        "status": "processesing ingestion",
        "message": "Ingestion process started in the background. Check /ingest/status for progress..."
    }

@router.get("/ingest/status", response_model=IngestStatusResponse)
async def get_status():
    collection_data = get_active_collection(["collection_name", "updated_at", "chunking_config"])
    return IngestStatusResponse (
        status = ingestion_status["status"],
        message = ingestion_status["message"],
        config = collection_data
    )