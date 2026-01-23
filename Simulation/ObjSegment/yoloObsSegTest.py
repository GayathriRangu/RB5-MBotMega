import cv2
import numpy as np
from ultralytics import YOLO

# Load pretrained YOLOv8 model
model = YOLO("yolov8n.pt")  # nano = fastest, good enough

# Load image
img_path = "test113.jpg"
img = cv2.imread(img_path)
assert img is not None, "Image not found"

# Run inference
results = model(img)[0]

# Colors for visualization
np.random.seed(42)
colors = np.random.randint(0, 255, size=(80, 3), dtype="uint8")

detections = []

for box in results.boxes:
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    cls_id = int(box.cls[0])
    conf = float(box.conf[0])
    label = model.names[cls_id]

    detections.append({
        "label": label,
        "confidence": conf,
        "bbox": (x1, y1, x2, y2)
    })

    color = colors[cls_id].tolist()
    cv2.rectangle(img, (x1,y1), (x2,y2), color, 2)
    cv2.putText(
        img,
        f"{label} {conf:.2f}",
        (x1, y1 - 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        color,
        2
    )

# Show result
cv2.imshow("YOLO Indoor Detection", img)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Print detections (important for RL)
print("\nDetected Objects:")
for d in detections:
    print(d)
