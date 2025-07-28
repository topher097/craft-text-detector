"""Note: Use the python 3.9 environment to run this script."""

from craft_text_detector import load_craftnet_model
import torch

# Load the PyTorch Model
model = load_craftnet_model(cuda=False)
input_shape = (1, 3, 1280, 1280)

# Convert to ONNX
onnx_model_path = "craft_mlt_25k.onnx"
torch.onnx.export(
    model,
    torch.randn(input_shape),
    onnx_model_path,
    export_params=True,
    opset_version=11,
    do_constant_folding=True,
    input_names=["input"],
    output_names=["output"],
)
