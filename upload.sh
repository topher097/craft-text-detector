aws s3 cp ./craft_mlt_25k_256x256.onnx s3://pgi-models/text_detection/20250728_onnx/ 
aws s3 cp ./craft_mlt_25k_512x512.onnx s3://pgi-models/text_detection/20250728_onnx/ 
aws s3 cp ./craft_mlt_25k_640x480.onnx s3://pgi-models/text_detection/20250728_onnx/ 
aws s3 cp ./craft_mlt_25k_1280x1280.onnx s3://pgi-models/text_detection/20250728_onnx/ 

aws s3 cp ./saved_model_256x256/ s3://pgi-models/text_detection/20250728_tf_256x256 --recursive
aws s3 cp ./saved_model_512x512/ s3://pgi-models/text_detection/20250728_tf_512x512 --recursive
aws s3 cp ./saved_model_640x480/ s3://pgi-models/text_detection/20250728_tf_640x480 --recursive
aws s3 cp ./saved_model_1280x1280/ s3://pgi-models/text_detection/20250728_tf_1280x1280 --recursive


