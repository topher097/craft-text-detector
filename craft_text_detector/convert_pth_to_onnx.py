"""Note: Use the python 3.9 environment to run this script."""


def convert(
    height: int = 512,
    width: int = 512,
) -> None:
    from craft_text_detector import load_craftnet_model

    # Load the PyTorch Model
    model = load_craftnet_model(cuda=False)
    input_shape = (
        1,
        3,
        height,
        width,
    )  # Note that the input shape is (batch_size, channels, height, width)

    # Convert to ONNX
    onnx_model_path = f"craft_mlt_25k_{width}x{height}.onnx"
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


if __name__ == "__main__":
    # Make sure the correct versions of things are being used
    import sys
    import argparse

    try:
        import torch
    except ImportError:
        raise ImportError("Please install torch: pip install torch")
    if "3.9" not in sys.version:
        raise ImportError("Please use Python 3.9 to run this script")

    # Have argument for the input size of the model
    parser = argparse.ArgumentParser(description="Convert CRAFT model to ONNX format.")
    parser.add_argument(
        "--input_shape",
        type=int,
        nargs=2,
        default=[512, 512],
        help="Input shape for the model (width, height) in pixels. Default is 512x512.",
    )
    args = parser.parse_args()
    width, height = args.input_shape
    convert(height=height, width=width)
    print(f"Converted CRAFT model to ONNX format with input shape {width}x{height}.")
