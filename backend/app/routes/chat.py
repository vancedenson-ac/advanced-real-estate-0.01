"""RAG chat endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..services.crud import (
    create_conversation,
    add_message,
    get_conversation_messages,
    search_similar_images,
    search_similar_messages
)
from ..services.embeddings import get_text_embedding
from ..schemas.prediction import ChatRequest, ChatResponse

router = APIRouter()


def build_rag_prompt(
    user_message: str,
    similar_images: list,
    similar_messages: list,
    listing_id: Optional[int] = None,
    listing_price: Optional[float] = None,
    listing_zip: Optional[str] = None
) -> str:
    """Build RAG prompt with context."""
    prompt_parts = [
        "You are a home improvement advisor. Use only the following context and answer concisely.\n",
    ]
    
    if listing_id:
        prompt_parts.append(f"Listing metadata:\n- Listing ID: {listing_id}\n")
        if listing_price:
            prompt_parts.append(f"- Price: ${listing_price:,.0f}\n")
        if listing_zip:
            prompt_parts.append(f"- Location: {listing_zip}\n")
        prompt_parts.append("\n")
    
    if similar_images:
        prompt_parts.append(f"Top {len(similar_images)} relevant images (summaries):\n")
        for i, img in enumerate(similar_images, 1):
            prompt_parts.append(
                f"{i}) Image id {img['id']} - room: {img.get('room_type', 'unknown')} "
                f"(conf={img.get('room_confidence', 0):.2f}), "
                f"features: {img.get('features', [])}, "
                f"condition: {img.get('condition_score', 0):.2f}, "
                f"light: {img.get('natural_light_score', 0):.2f}\n"
            )
        prompt_parts.append("\n")
    
    if similar_messages:
        prompt_parts.append(f"Relevant past conversation context:\n")
        for msg in similar_messages[:3]:  # Top 3 messages
            prompt_parts.append(f"- {msg['role']}: {msg['text'][:200]}...\n")
        prompt_parts.append("\n")
    
    prompt_parts.append(f"User question:\n{user_message}\n\n")
    prompt_parts.append(
        "Instruction:\n"
        "Provide up to 5 prioritized improvement suggestions with estimated cost brackets "
        "(Low: <$500, Medium: $500–$3k, High: >$3k) and expected ROI qualitative (Low/Medium/High). "
        "If insufficient data, ask for clarification."
    )
    
    return "".join(prompt_parts)


def call_llm(prompt: str) -> str:
    """
    Call LLM with prompt.
    
    Stub implementation - replace with actual LLM API call.
    """
    # In production, this would call:
    # - OpenAI API: openai.ChatCompletion.create(...)
    # - Anthropic API: anthropic.Anthropic().messages.create(...)
    # - Or hosted LLM service
    
    # Stub response
    return (
        "Top 3 quick improvements:\n"
        "1) Repaint kitchen cabinets (Medium cost, High ROI)\n"
        "2) Replace dated hardware & fixtures (Low cost, Medium ROI)\n"
        "3) Stage with a few potted plants & lighting (Low cost, Medium ROI)\n"
        "Estimated combined cost: $800–$2,500. Would you like a materials & labor breakdown for option #1?"
    )


@router.post("/chat/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    RAG-enabled chat endpoint.
    Retrieves relevant images and messages, builds prompt, calls LLM.
    """
    try:
        # Get or create conversation
        if request.conversation_id:
            conversation_id = request.conversation_id
        else:
            conversation_id = create_conversation(
                db=db,
                user_id=request.user_id,
                listing_id=request.listing_id
            )
        
        # Convert user message to embedding
        user_embedding = get_text_embedding(request.message)
        
        # Retrieve similar images using text embedding search
        # For text queries, we search using text_embedding column which is 1536-d
        similar_images = search_similar_images(
            db=db,
            query_embedding=user_embedding,  # 1536-d text embedding
            k=6,
            listing_id=request.listing_id,
            use_text_embedding=True  # Use text_embedding column for text queries
        )
        
        # Retrieve similar past messages
        similar_messages = search_similar_messages(
            db=db,
            query_embedding=user_embedding,
            conversation_id=conversation_id,
            k=5
        )
        
        # Get listing metadata if listing_id provided
        listing_price = None
        listing_zip = None
        if request.listing_id:
            from ..database import Listing
            listing = db.query(Listing).filter(Listing.id == request.listing_id).first()
            if listing:
                listing_price = listing.price
                listing_zip = listing.zip_code
        
        # Build RAG prompt
        prompt = build_rag_prompt(
            user_message=request.message,
            similar_images=similar_images,
            similar_messages=similar_messages,
            listing_id=request.listing_id,
            listing_price=listing_price,
            listing_zip=listing_zip
        )
        
        # Call LLM
        reply = call_llm(prompt)
        
        # Store user message
        add_message(
            db=db,
            conversation_id=conversation_id,
            role="user",
            text=request.message,
            embedding=user_embedding
        )
        
        # Store assistant reply
        assistant_embedding = get_text_embedding(reply)
        add_message(
            db=db,
            conversation_id=conversation_id,
            role="assistant",
            text=reply,
            embedding=assistant_embedding
        )
        
        return ChatResponse(
            conversation_id=conversation_id,
            reply=reply,
            context_used={
                "images_count": len(similar_images),
                "messages_count": len(similar_messages)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get all messages for a conversation."""
    messages = get_conversation_messages(db, conversation_id)
    return {"conversation_id": conversation_id, "messages": messages}

