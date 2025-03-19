import os
import cv2
import json
import logging
from typing import Optional, Dict
from confluent_kafka import Producer
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoPreprocessor:
    def __init__(
        self,
        kafka_config: Dict,
        frames_topic: str = 'frames',
        frame_rate: int = 30
    ):
        """Initialize the video preprocessor with Kafka configuration.

        Args:
            kafka_config: Kafka producer configuration including security settings
            frames_topic: Kafka topic for publishing frames
            frame_rate: Target frame rate for processing
        """
        self.producer = Producer(kafka_config)
        self.frames_topic = frames_topic
        self.frame_rate = frame_rate
        self.frame_count = 0

    def delivery_report(self, err, msg):
        """Callback for Kafka producer to report delivery status."""
        if err is not None:
            logger.error(f'Message delivery failed: {err}')
        else:
            logger.debug(f'Message delivered to {msg.topic()} [{msg.partition()}]')

    def process_frame(self, frame, prompt: str):
        """Process a single frame and publish to Kafka.

        Args:
            frame: OpenCV frame
            prompt: Text prompt for object detection
        """
        try:
            # Encode frame as JPEG
            _, encoded_frame = cv2.imencode('.jpg', frame)
            frame_bytes = encoded_frame.tobytes()

            # Prepare message payload
            message = {
                'frame': frame_bytes,
                'prompt': prompt,
                'frame_id': self.frame_count
            }

            # Publish to Kafka
            self.producer.produce(
                self.frames_topic,
                key=str(self.frame_count),
                value=json.dumps(message),
                callback=self.delivery_report
            )
            self.producer.poll(0)
            self.frame_count += 1

        except Exception as e:
            logger.error(f'Error processing frame: {e}')

    def process_video(self, video_source: str, prompt: str):
        """Process video stream and publish frames to Kafka.

        Args:
            video_source: Path to video file or camera index
            prompt: Text prompt for object detection
        """
        try:
            # Open video capture
            cap = cv2.VideoCapture(video_source)
            if not cap.isOpened():
                raise ValueError(f'Failed to open video source: {video_source}')

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                self.process_frame(frame, prompt)
                self.producer.flush()

        except Exception as e:
            logger.error(f'Error processing video: {e}')
        finally:
            if 'cap' in locals():
                cap.release()

def main():
    # Kafka configuration with SSL/TLS
    kafka_config = {
        'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
        'security.protocol': 'SSL',
        'ssl.ca.location': '/security/kafka.crt',
        'ssl.keystore.location': '/security/kafka.key',
        'ssl.keystore.password': os.getenv('KAFKA_SSL_KEYSTORE_PASSWORD')
    }

    # Initialize preprocessor
    preprocessor = VideoPreprocessor(kafka_config)

    # Process video with detection prompt
    video_source = os.getenv('VIDEO_SOURCE', '0')  # Default to webcam
    detection_prompt = os.getenv('DETECTION_PROMPT', 'detect person, car, bike')
    
    preprocessor.process_video(video_source, detection_prompt)

if __name__ == '__main__':
    main()