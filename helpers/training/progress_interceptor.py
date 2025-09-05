import requests
import os
import logging

logger = logging.getLogger("ProgressInterceptor")


class ProgressInterceptor:
    def __init__(self, train_id):
        self.train_id = train_id
        self.api_key = os.getenv("API_KEY")
        self.api_base_url = os.getenv("BASE_URL")
        self.last_reported_progress = -1  # Track last reported progress to avoid duplicate calls
        
        # Validate required environment variables
        if not self.api_key:
            logger.warning("API_KEY environment variable not set. Progress updates will be disabled.")
        if not self.api_base_url:
            logger.warning("BASE_URL environment variable not set. Progress updates will be disabled.")
            
        logger.info(f"ProgressInterceptor initialized for train_id: {self.train_id}")

    def send_training_progress(self, value, max_value):
        """
        Send training progress update to the API.
        
        Args:
            value (int): Current training step
            max_value (int): Maximum training steps
        """
        if not self.api_key or not self.api_base_url:
            return  # Skip if not configured
            
        if max_value <= 0:
            logger.warning("Invalid max_value for progress calculation")
            return
            
        # Calculate progress percentage
        if max_value < 100:
            progress = int((value / max_value) * 100)
            progress = min(90, progress)
        else:
            progress_step = max_value // 100
            if progress_step > 0 and value % progress_step == 0:
                progress = value // progress_step
                progress = min(90, progress)
            else:
                return  # Skip this update if not at a reporting interval
        
        # Only send update if progress has changed
        if progress != self.last_reported_progress:
            self._post_progress(progress)
            self.last_reported_progress = progress

    def send_completion_progress(self):
        """Send 100% completion progress."""
        if self.api_key and self.api_base_url:
            self._post_progress(100)

    def _post_progress(self, progress):
        """
        Internal method to POST progress to the API.
        
        Args:
            progress (int): Progress percentage (0-100)
        """
        url = f"{self.api_base_url}/{self.train_id}/update_training_progress/"

        headers = {
            "authorization": f"{self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {"progress": progress}

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Progress updated to {progress}%")
        except requests.RequestException as e:
            logger.error(f"Failed to update progress: {e}")
