import onnx_tf
import onnx
from craft_text_detector.convert_pth_to_onnx import onnx_model_path

# Convert ONNX to TensorFlow
onnx_model = onnx.load(onnx_model_path)
tf_model = onnx_tf.backend.prepare(onnx_model)

# Save the TensorFlow model as a SavedModel
tf_model_path = "craft_text_detector.pb"
tf_model.export_graph(tf_model_path)
