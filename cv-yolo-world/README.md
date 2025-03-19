# YOLO-World Real-Time Object Detection System

A distributed system for real-time object detection using YOLO-World with Kafka-based video stream processing.

## System Architecture

### Overview
The system consists of three main components:
1. **Video Preprocessor**: Captures and processes video frames
2. **Kafka Message Broker**: Handles frame distribution with SSL/TLS security
3. **YOLO-World Inference Workers**: Perform parallel object detection

### Components

#### Video Preprocessor
- Captures video frames from camera/file
- Encodes frames as JPEG
- Publishes frames to Kafka topic with custom prompts
- Supports configurable frame rate

#### Kafka Message Broker
- Secure communication with SSL/TLS
- Multi-partition topic for parallel processing
- Configurable retention and replication
- Message delivery guarantees

#### YOLO-World Inference
- Multiple parallel workers
- Dynamic prompt-based object detection
- GPU acceleration support
- Encrypted model loading

## Security Features

### SSL/TLS Encryption
- Kafka broker SSL configuration
- Client certificate authentication
- Encrypted communication channels

### Model Protection
- Model file encryption using Fernet
- Secure key management
- Temporary decryption for inference

## Installation

### Prerequisites
- Docker and Docker Compose
- CUDA-capable GPU (recommended)
- SSL certificates and keys

### Environment Setup
1. Set up SSL certificates in `./security/`:
   - kafka.crt
   - kafka.key
   - kafka.truststore.jks
   - kafka.keystore.jks

2. Configure environment variables:
```bash
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_SSL_KEYSTORE_PASSWORD=your_password
VIDEO_SOURCE=0  # Use 0 for webcam or file path
DETECTION_PROMPT="detect person, car, bike"
MODEL_ENCRYPTION_KEY=your_encryption_key
```

## Deployment

### Using Docker Compose
```bash
# Start the system
docker-compose up -d

# Scale inference workers
docker-compose up -d --scale inference=4

# Monitor logs
docker-compose logs -f
```

## Usage

### Basic Usage
1. Start the system with default configuration:
```bash
docker-compose up -d
```

2. Monitor detection results:
```bash
docker-compose logs -f inference
```

### Custom Detection
1. Modify detection prompt:
```bash
export DETECTION_PROMPT="detect cat, dog, bird"
docker-compose up -d
```

2. Use custom video source:
```bash
export VIDEO_SOURCE=/path/to/video.mp4
docker-compose up -d
```

## Configuration

### Video Preprocessor
- `frame_rate`: Frame processing rate (default: 30)
- `frames_topic`: Kafka topic for frames (default: 'frames')

### Inference Workers
- `model_path`: Path to YOLO-World model
- `partition`: Kafka partition assignment
- `detections_topic`: Output topic (default: 'detections')

### Kafka Settings
- `NUM_PARTITIONS`: Number of topic partitions (default: 4)
- `LOG_RETENTION_HOURS`: Message retention period (default: 24)

## Performance Optimization

### Scaling
- Increase inference workers for higher throughput
- Adjust Kafka partitions for parallelism
- Configure frame rate for resource usage

### GPU Utilization
- Enable CUDA for faster inference
- Monitor GPU memory usage
- Balance worker count with GPU resources

## Troubleshooting

### Common Issues
1. Kafka Connection Failures
   - Verify SSL certificate paths
   - Check network connectivity
   - Validate broker address

2. Model Loading Errors
   - Confirm encryption key
   - Check model file permissions
   - Verify CUDA availability

3. Frame Processing Issues
   - Check video source accessibility
   - Monitor system resources
   - Verify Kafka topic configuration

## API Reference

### VideoPreprocessor
```python
class VideoPreprocessor:
    def __init__(self, kafka_config: Dict, frames_topic: str = 'frames', frame_rate: int = 30)
    def process_video(self, video_source: str, prompt: str)
    def process_frame(self, frame, prompt: str)
```

### YOLOWorldInference
```python
class YOLOWorldInference:
    def __init__(self, kafka_config: Dict, model_path: str, frames_topic: str = 'frames',
                 detections_topic: str = 'detections', partition: int = 0)
    def process_frame(self, frame_data: Dict) -> Dict
    def run(self)
```

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Submit a pull request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- YOLO-World for object detection
- Apache Kafka for stream processing
- OpenCV for video processing