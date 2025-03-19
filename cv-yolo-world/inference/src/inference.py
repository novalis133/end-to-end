import os
import json
import torch
import logging
from typing import Dict, List, Tuple
from confluent_kafka import Consumer, Producer
from ultralytics import YOLO
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YOLOWorldInference:
    def __init__(
        self,
        kafka_config: Dict,
        model_path: str,
        frames_topic: str = 'frames',
        detections_topic: str = 'detections',
        partition: int = 0
    ):
        """Initialize YOLO-World inference worker.

        Args:
            kafka_config: Kafka configuration for consumer and producer
            model_path: Path to the YOLO-World model file
            frames_topic: Kafka topic for consuming frames
            detections_topic: Kafka topic for publishing detections
            partition: Kafka partition to consume from
        """
        self.consumer = Consumer({
            **kafka_config,
            'group.id': 'yolo_inference_group',
            'auto.offset.reset': 'latest'
        })
        self.producer = Producer(kafka_config)
        self.frames_topic = frames_topic
        self.detections_topic = detections_topic
        
        # Assign specific partition
        self.consumer.assign([{'topic': frames_topic, 'partition': partition}])
        
        # Load YOLO-World model
        self.model = self._load_model(model_path)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f'Using device: {self.device}')

    def _load_model(self, model_path: str) -> YOLO:
        """Load and decrypt YOLO-World model."""
        try:
            # Decrypt model if encrypted
            if model_path.endswith('.enc'):
                key = os.getenv('MODEL_ENCRYPTION_KEY')
                if not key:
                    raise ValueError('Model encryption key not found')
                    
                f = Fernet(key)
                with open(model_path, 'rb') as encrypted_file:
                    encrypted_data = encrypted_file.read()
                decrypted_data = f.decrypt(encrypted_data)
                
                temp_model_path = '/tmp/model.pt'
                with open(temp_model_path, 'wb') as decrypted_file:
                    decrypted_file.write(decrypted_data)
                model_path = temp_model_path

            return YOLO(model_path)
        except Exception as e:
            logger.error(f'Error loading model: {e}')
            raise

    def process_frame(self, frame_data: Dict) -> Dict:
        """Process a single frame with YOLO-World.

        Args:
            frame_data: Dictionary containing frame bytes and prompt

        Returns:
            Dictionary containing detection results
        """
        try:
            # Convert frame bytes to tensor
            frame = torch.from_numpy(frame_data['frame'])
            prompt = frame_data['prompt']
            frame_id = frame_data['frame_id']

            # Run inference with prompt
            results = self.model(frame, prompt=prompt)
            
            # Extract detections
            detections = {
                'frame_id': frame_id,
                'boxes': results[0].boxes.xyxy.tolist(),
                'labels': results[0].boxes.cls.tolist(),
                'confidences': results[0].boxes.conf.tolist()
            }
            
            return detections

        except Exception as e:
            logger.error(f'Error processing frame: {e}')
            return None

    def run(self):
        """Main inference loop."""
        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    logger.error(f'Consumer error: {msg.error()}')
                    continue

                # Process message
                try:
                    frame_data = json.loads(msg.value())
                    detections = self.process_frame(frame_data)
                    
                    if detections:
                        # Publish results
                        self.producer.produce(
                            self.detections_topic,
                            key=str(detections['frame_id']),
                            value=json.dumps(detections)
                        )
                        self.producer.poll(0)

                except Exception as e:
                    logger.error(f'Error processing message: {e}')

        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()

def main():
    # Kafka configuration with SSL/TLS
    kafka_config = {
        'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
        'security.protocol': 'SSL',
        'ssl.ca.location': '/security/kafka.crt',
        'ssl.keystore.location': '/security/kafka.key',
        'ssl.keystore.password': os.getenv('KAFKA_SSL_KEYSTORE_PASSWORD')
    }

    # Initialize inference worker
    partition = int(os.getenv('KAFKA_PARTITION', '0'))
    model_path = os.getenv('MODEL_PATH', '/models/yolo_world_m.pt.enc')
    
    worker = YOLOWorldInference(
        kafka_config=kafka_config,
        model_path=model_path,
        partition=partition
    )
    
    worker.run()

if __name__ == '__main__':
    main()