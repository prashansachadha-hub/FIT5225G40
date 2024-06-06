import numpy as np
import cv2
import os

conf_threshold = 0.6
nms_threshold = 0.1

def load_labels(labels_file):
    labels_path = os.path.sep.join([yolo_path, labels_file])
    LABELS = open(labels_path).read().strip().split("\n")
    return LABELS

def load_weights(weights_file):
    weights_path = os.path.sep.join([yolo_path, weights_file])
    return weights_path

def load_config(config_file):
    config_path = os.path.sep.join([yolo_path, config_file])
    return config_path

def load_model(config_path, weights_path):
    print("[INFO] Loading YOLO from disk...")
    net = cv2.dnn.readNetFromDarknet(config_path, weights_path)
    return net

def perform_prediction(image, net, LABELS):
    (H, W) = image.shape[:2]
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layer_outputs = net.forward(output_layers)

    boxes = []
    confidences = []
    classIDs = []

    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]

            if confidence > conf_threshold:
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))
                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)

    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
    results = []
    if len(indices) > 0:
        for i in indices.flatten():
            results.append({
                "label": LABELS[classIDs[i]],
                "accuracy": confidences[i],
                "rectangle": {
                    "height": boxes[i][3],
                    "left": boxes[i][0],
                    "top": boxes[i][1],
                    "width": boxes[i][2]
                }
            })
    return results

yolo_path = "/opt/yolo_configs"
labels_file = "coco.names"
config_file = "yolov3-tiny.cfg"
weights_file = "yolov3-tiny.weights"

LABELS = load_labels(labels_file)
CFG = load_config(config_file)
Weights = load_weights(weights_file)
    
def detect_image_bytes(image_bytes):
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    net = load_model(CFG, Weights)
    results = perform_prediction(image, net, LABELS)
    tags = [result['label'] for result in results]
    return tags