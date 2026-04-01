from fastapi import APIRouter, HTTPException
from backend.app.core.twin import DigitalTwin


router = APIRouter(prefix="/delete", tags=["Cognition"])

# 🔥 Singleton brain
twin = DigitalTwin()


@router.delete("/memory")
def delete_all_memory():
    """
    Deletes all long-term (and optionally short-term) memories
    of the Digital Twin.
    """
    try:
        # 🔹 Delete Long-Term Memory
        if hasattr(twin, "delete_ltm_memories"):
            twin.delete_ltm_memories()

        # 🔹 Optional: Delete Short-Term Memory
        if hasattr(twin, "delete_stm_memories"):
            twin.delete_stm_memories()

        return {
            "status": "success",
            "message": "All memories deleted successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete memories: {str(e)}"
        )
