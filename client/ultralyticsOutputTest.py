from ultralytics import YOLO

# Load a pretrained YOLO model (e.g., YOLOv8n for object detection)
# The 'n' stands for nano, a smaller, faster model
model = YOLO("yolov8n.pt")

# Run inference on a source (image, video, or stream)
# The results object contains bounding boxes, classes, and confidence scores
results = model("https://ultralytics.com/images/bus.jpg")

# Process results and visualize (optional)
for result in results:
    boxes = result.boxes  # Bounding box data
    # Further analysis can be done here, such as printing coordinates, class names, etc.
