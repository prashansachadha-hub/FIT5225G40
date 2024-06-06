import numpy as np
import cv2

# Load YOLOv3 model weights and configuration file
net = cv2.dnn.readNet(
    "/opt/yolo_configs/yolov3-tiny.weights", "/opt/yolo_configs/yolov3-tiny.cfg"
)
classes = []


# Load class labels (from COCO dataset)
with open("/opt/yolo_configs/coco.names", "r") as f:
    classes = f.read().strip().split("\n")


def detect_image_bytes(image_bytes):
    objects = []
    # Convert binary data to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    # Decode numpy array to image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Prepare the blob for the network by resizing and normalizing
    blob = cv2.dnn.blobFromImage(img, 1 / 255, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    # Forward pass through the network
    outs = net.forward(net.getUnconnectedOutLayersNames())

    # Process network output
    for out in outs:
        for detection in out:
            scores = detection[5:]  # scores of all classes
            class_id = np.argmax(scores)  # class with highest score
            confidence = scores[class_id]  # confidence of the class

            if confidence >= 0.6:
                # Calculate bounding box dimensions
                center_x = int(detection[0] * img.shape[1])
                center_y = int(detection[1] * img.shape[0])
                width = int(detection[2] * img.shape[1])
                height = int(detection[3] * img.shape[0])
                x = int(center_x - width / 2)
                y = int(center_y - height / 2)

                # Append detected object details to the list
                objects.append(
                    {
                        "label": classes[class_id],
                        "accuracy": float(confidence),
                        "rectangle": {
                            "height": height,
                            "left": x,
                            "top": y,
                            "width": width,
                        },
                    }
                )
    tags = [obj['label'] for obj in objects]
    return tags