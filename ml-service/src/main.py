#!/usr/bin/env python3
"""
ML Service - Facial Recognition API

FastAPI-based service providing face recognition endpoints.
"""

import os
import logging
from typing import List, Optional

import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from face_mediapipe import FaceRecognitionEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ML Service - Facial Recognition API",
    description="Machine learning service for facial recognition and authentication",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize face recognition engine
face_engine = FaceRecognitionEngine(tolerance=0.6)


# Pydantic models
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class ExtractEmbeddingResponse(BaseModel):
    success: bool
    embedding: Optional[List[float]] = None
    quality: str
    message: str


class CompareFacesRequest(BaseModel):
    embedding1: List[float]
    embedding2: List[float]


class CompareFacesResponse(BaseModel):
    success: bool
    is_match: bool
    distance: float
    confidence: float


class AuthenticateRequest(BaseModel):
    test_embedding: List[float]
    stored_embeddings: List[List[float]]


class AuthenticateResponse(BaseModel):
    success: bool
    is_authenticated: bool
    confidence: float
    best_match_index: Optional[int] = None
    message: str


# API Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="ml-service",
        version="1.0.0"
    )


@app.post("/extract-embedding", response_model=ExtractEmbeddingResponse)
async def extract_embedding(file: UploadFile = File(...)):
    """
    Extract face embedding from uploaded image

    Args:
        file: Image file (JPEG/PNG)

    Returns:
        Face embedding and quality assessment
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image (JPEG/PNG)"
            )

        # Read image bytes
        image_bytes = await file.read()

        if len(image_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file uploaded"
            )

        # Verify image quality
        is_quality_ok, quality_level, quality_message = face_engine.verify_face_quality(image_bytes)

        if not is_quality_ok:
            return ExtractEmbeddingResponse(
                success=False,
                embedding=None,
                quality=quality_level,
                message=quality_message
            )

        # Extract face embedding
        embedding = face_engine.extract_embedding(image_bytes)

        if embedding is None:
            return ExtractEmbeddingResponse(
                success=False,
                embedding=None,
                quality="low",
                message="Failed to extract face embedding"
            )

        # Convert numpy array to list for JSON serialization
        embedding_list = embedding.tolist()

        return ExtractEmbeddingResponse(
            success=True,
            embedding=embedding_list,
            quality=quality_level,
            message=quality_message
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in extract_embedding: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        ) from e


@app.post("/compare-faces", response_model=CompareFacesResponse)
async def compare_faces(request: CompareFacesRequest):
    """
    Compare two face embeddings

    Args:
        request: Two face embeddings to compare

    Returns:
        Comparison result with match status and distance
    """
    try:
        # Convert lists back to numpy arrays
        embedding1 = np.array(request.embedding1)
        embedding2 = np.array(request.embedding2)

        # Validate embedding dimensions
        if len(embedding1) != 128 or len(embedding2) != 128:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Face embeddings must be 128-dimensional vectors"
            )

        # Compare faces
        is_match, distance = face_engine.compare_faces(embedding1, embedding2)

        # Calculate confidence (inverse of distance, clamped to 0-1)
        confidence = max(0.0, min(1.0, 1.0 - distance))

        return CompareFacesResponse(
            success=True,
            is_match=is_match,
            distance=distance,
            confidence=confidence
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in compare_faces: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        ) from e


@app.post("/authenticate", response_model=AuthenticateResponse)
async def authenticate_face(request: AuthenticateRequest):
    """
    Authenticate a face against stored embeddings

    Args:
        request: Test embedding and list of stored embeddings

    Returns:
        Authentication result
    """
    try:
        # Convert lists to numpy arrays
        test_embedding = np.array(request.test_embedding)
        stored_embeddings = [np.array(emb) for emb in request.stored_embeddings]

        # Validate embedding dimensions
        if len(test_embedding) != 128:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Test embedding must be a 128-dimensional vector"
            )

        for i, emb in enumerate(stored_embeddings):
            if len(emb) != 128:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stored embedding {i} must be a 128-dimensional vector"
                )

        if not stored_embeddings:
            return AuthenticateResponse(
                success=True,
                is_authenticated=False,
                confidence=0.0,
                best_match_index=None,
                message="No stored embeddings to compare against"
            )

        # Perform authentication
        is_match, best_distance, best_match_index = face_engine.compare_face_to_embeddings(
            test_embedding, stored_embeddings
        )

        # Calculate confidence
        confidence = max(0.0, min(1.0, 1.0 - best_distance))

        message = "Authentication successful" if is_match else "No matching face found"

        return AuthenticateResponse(
            success=True,
            is_authenticated=is_match,
            confidence=confidence,
            best_match_index=best_match_index if is_match else None,
            message=message
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in authenticate_face: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        ) from e


def main():
    """Start the ML service"""
    host = os.getenv('ML_SERVICE_HOST', '0.0.0.0')
    port = int(os.getenv('ML_SERVICE_PORT', '8081'))

    logger.info("Starting ML service on %s:%s", host, port)

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,  # Set to True for development
        log_level="info"
    )


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
