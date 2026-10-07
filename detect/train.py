from ultralytics import YOLO

model = YOLO("detect/yolo26n.pt")

train_results = model.train(
    data="coco8.yaml",
    epochs=64,
    imgsz=640,
    device="cpu",
)

metrics = model.val()

results = model("path/to/image.jpg")  # Predict on an image
results[0].show()  # Display results

# Export the model to ONNX format for deployment
path = model.export(format="onnx")  # Returns the path to the exported model