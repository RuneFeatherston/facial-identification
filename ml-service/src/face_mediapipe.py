"""
Face Recognition Engine

Core face recognition functionality using MediaPipe.
"""

import logging
from typing import List, Optional, Tuple

import cv2
import numpy as np
import mediapipe as mp

logger = logging.getLogger(__name__)


class FaceRecognitionEngine:
    """Core face recognition functionality using MediaPipe"""

    def __init__(self, tolerance: float = 0.6):
        """
        Initialize face recognition engine

        Args:
            tolerance: Face matching tolerance (lower = more strict)
        """
        self.tolerance = tolerance
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.5
        )
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
        )
        logger.info("FaceRecognitionEngine initialized with tolerance=%s", tolerance)

    def extract_embedding(self, image_bytes: bytes) -> Optional[np.ndarray]:
        """
        Extract face embedding from image bytes

        Args:
            image_bytes: Image data as bytes

        Returns:
            Face embedding as numpy array or None if no face found
        """
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # pylint: disable=no-member

            if image is None:
                logger.error("Failed to decode image")
                return None

            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # pylint: disable=no-member

            # Detect faces using MediaPipe
            results = self.face_detection.process(rgb_image)

            if not results.detections:
                logger.warning("No faces detected in image")
                return None

            # Get face mesh for the first detected face
            mesh_results = self.face_mesh.process(rgb_image)

            if not mesh_results.multi_face_landmarks:
                logger.warning("No face landmarks detected")
                return None

            # Extract facial landmarks as embedding
            face_landmarks = mesh_results.multi_face_landmarks[0]

            # Convert landmarks to feature vector
            embedding = self._landmarks_to_embedding(face_landmarks, rgb_image.shape)

            logger.info(
                "Successfully extracted face embedding with %s features", len(embedding)
            )
            return embedding

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error extracting face embedding: %s", e)
            return None

    def _landmarks_to_embedding(self, landmarks, image_shape) -> np.ndarray:  # pylint: disable=unused-argument
        """
        Convert face landmarks to a numerical embedding

        Args:
            landmarks: MediaPipe face landmarks
            image_shape: Shape of the input image

        Returns:
            Numerical embedding vector
        """
        # Extract key facial landmarks and normalize them
        # Note: height, width not used as we normalize to 0-1 range anyway

        # Key facial points for creating embedding
        key_points = []
        for landmark in landmarks.landmark:
            # Normalize coordinates to 0-1 range
            x = landmark.x
            y = landmark.y
            z = landmark.z if hasattr(landmark, "z") else 0
            key_points.extend([x, y, z])

        # Create a fixed-size embedding from the first 128 features
        embedding = np.array(key_points[:128], dtype=np.float64)

        # Pad with zeros if we have fewer than 128 features
        if len(embedding) < 128:
            padding = np.zeros(128 - len(embedding))
            embedding = np.concatenate([embedding, padding])

        return embedding

    def compare_faces(
        self, known_embedding: np.ndarray, test_embedding: np.ndarray
    ) -> Tuple[bool, float]:
        """
        Compare two face embeddings

        Args:
            known_embedding: Known face embedding
            test_embedding: Test face embedding

        Returns:
            Tuple of (is_match, confidence_score)
        """
        try:
            # Calculate Euclidean distance between embeddings
            distance = np.linalg.norm(known_embedding - test_embedding)

            # Convert distance to similarity score (0-1, higher is better)
            similarity = 1.0 / (1.0 + distance)

            # Determine if it's a match based on tolerance
            is_match = distance <= self.tolerance

            logger.debug(
                "Face comparison: distance=%.4f, similarity=%.4f, match=%s",
                distance, similarity, is_match
            )

            return is_match, similarity

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error comparing faces: %s", e)
            return False, 0.0

    def verify_face_quality(self, image_bytes: bytes) -> Tuple[bool, str]:  # pylint: disable=too-many-return-statements
        """
        Verify if the image has good quality for face recognition

        Args:
            image_bytes: Image data as bytes

        Returns:
            Tuple of (is_good_quality, quality_message)
        """
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # pylint: disable=no-member

            if image is None:
                return False, "Invalid image format"

            # Check image dimensions
            height, width = image.shape[:2]
            if width < 100 or height < 100:
                return False, "Image too small (minimum 100x100)"

            # Convert to RGB for MediaPipe
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # pylint: disable=no-member

            # Detect faces
            results = self.face_detection.process(rgb_image)

            if not results.detections:
                return False, "No face detected"

            if len(results.detections) > 1:
                return False, "Multiple faces detected"

            # Check face size relative to image
            detection = results.detections[0]
            bbox = detection.location_data.relative_bounding_box

            face_width = bbox.width * width
            face_height = bbox.height * height

            if face_width < 50 or face_height < 50:
                return False, "Face too small in image"

            # Check if face takes up reasonable portion of image
            face_area_ratio = (face_width * face_height) / (width * height)
            if face_area_ratio < 0.05:
                return False, "Face too small relative to image"

            return True, "Good quality"

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error verifying face quality: %s", e)
            return False, f"Quality check failed: {str(e)}"

    def compare_face_to_embeddings(
        self, test_embedding: np.ndarray, stored_embeddings: List[np.ndarray]
    ) -> Tuple[bool, float, Optional[int]]:
        """
        Compare a test embedding against multiple stored embeddings

        Args:
            test_embedding: Face embedding to test
            stored_embeddings: List of known face embeddings

        Returns:
            Tuple of (is_match, best_confidence, best_match_index)
        """
        if not stored_embeddings:
            return False, 0.0, None

        best_confidence = 0.0
        best_match_index = None
        is_match = False

        for i, stored_embedding in enumerate(stored_embeddings):
            match, confidence = self.compare_faces(stored_embedding, test_embedding)

            if confidence > best_confidence:
                best_confidence = confidence
                best_match_index = i
                if match:
                    is_match = True

        logger.info(
            "Best match: index=%s, confidence=%.4f, match=%s",
            best_match_index, best_confidence, is_match
        )

        return is_match, best_confidence, best_match_index
