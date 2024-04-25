import cv2
import numpy as np
import onnxruntime as ort
from janken_functions import hands_dic

class Config():
    def __init__(self, model, conf_thres, iou_thres):
        self.model = model
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres


class YOLOv8:
    """YOLOv8 object detection model class for handling inference and visualization."""

    def __init__(self, args):
        """
        Initializes an instance of the YOLOv8 class.

        Args:
            onnx_model: Path to the ONNX model.
            input_image: Path to the input image.
            confidence_thres: Confidence threshold for filtering detections.
            iou_thres: IoU (Intersection over Union) threshold for non-maximum suppression.
        """
        self.onnx_model = args.model
        self.confidence_thres = args.conf_thres
        self.iou_thres = args.iou_thres

        # じゃんけんの手と出力ラベルの対応辞書(no detectionなし)
        self.classes = hands_dic

        # グーチョキパーの描画色
        self.color_palette = [[0, 0, 255], [255, 0, 0], [0, 255, 0]]

        self.setup()

        # 動作の高速化のため、ランダム生成画像を1枚推論
        dst_img = np.random.randint(256, size=(self.input_height, self.input_width, 3)).astype(np.uint8)
        self.main(dst_img)


    def setup(self):
        """
        Performs inference using an ONNX model and returns the output image with drawn detections.

        Returns:
            output_img: The output image with drawn detections.
        """

        

        # Create an inference session using the ONNX model and specify execution providers
        self.session = ort.InferenceSession(self.onnx_model, providers=['CPUExecutionProvider'])

        # モデルに入力すべきデータの形状取得
        self.model_inputs = self.session.get_inputs()

        # Store the shape of the input for later use
        self.input_shape =self. model_inputs[0].shape
        self.input_width = self.input_shape[2]
        self.input_height = self.input_shape[3]


    def preprocess(self, img):
        """
        Preprocesses the input image before performing inference.

        Returns:
            image_data: Preprocessed image data ready for inference.
        """
        # # Read the input image using OpenCV
        # self.img = cv2.imread(self.input_image)

        # Get the height and width of the input image
        self.img_height, self.img_width = img.shape[:2]

        # Convert the image color space from BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Resize the image to match the input shape
        img = cv2.resize(img, (self.input_width, self.input_height))

        # Normalize the image data by dividing it by 255.0
        image_data = np.array(img) / 255.0

        # Transpose the image to have the channel dimension as the first dimension
        image_data = np.transpose(image_data, (2, 0, 1))  # Channel first

        # Expand the dimensions of the image data to match the expected input shape
        image_data = np.expand_dims(image_data, axis=0).astype(np.float32)

        # Return the preprocessed image data
        return image_data


    def postprocess(self, input_image, output):
        """
        Performs post-processing on the model's output to extract bounding boxes, scores, and class IDs.

        Args:
            input_image (numpy.ndarray): The input image.
            output (numpy.ndarray): The output of the model.

        Returns:
            numpy.ndarray: The input image with detections drawn on it.
        """

        # Transpose and squeeze the output to match the expected shape
        outputs = np.transpose(np.squeeze(output[0]))

        # Get the number of rows in the outputs array
        rows = outputs.shape[0]

        # Lists to store the bounding boxes, scores, and class IDs of the detections
        boxes = []
        scores = []
        class_ids = []

        # Calculate the scaling factors for the bounding box coordinates
        x_factor = self.img_width / self.input_width
        y_factor = self.img_height / self.input_height

        # Iterate over each row in the outputs array
        for i in range(rows):
            # Extract the class scores from the current row
            classes_scores = outputs[i][4:]

            # Find the maximum score among the class scores
            max_score = np.amax(classes_scores)

            # If the maximum score is above the confidence threshold
            if max_score >= self.confidence_thres:
                # Get the class ID with the highest score
                class_id = np.argmax(classes_scores)

                # グーチョキパー以外を検出したらパスする
                if not class_id in hands_dic.keys():
                    continue

                # Extract the bounding box coordinates from the current row
                x, y, w, h = outputs[i][0], outputs[i][1], outputs[i][2], outputs[i][3]

                # Calculate the scaled coordinates of the bounding box
                left = int((x - w / 2) * x_factor)
                top = int((y - h / 2) * y_factor)
                width = int(w * x_factor)
                height = int(h * y_factor)

                # Add the class ID, score, and box coordinates to the respective lists
                class_ids.append(class_id)
                scores.append(max_score)
                boxes.append([left, top, width, height])

        # Apply non-maximum suppression to filter out overlapping bounding boxes
        # bbox被りを除く
        indices = cv2.dnn.NMSBoxes(boxes, scores, self.confidence_thres, self.iou_thres)

        detect_cls = []
        # Iterate over the selected indices after non-maximum suppression
        for i in indices:
            # Get the box, score, and class ID corresponding to the index
            box = boxes[i]
            score = scores[i]
            class_id = class_ids[i]
            detect_cls.append(class_id)

            # Draw the detection on the input image
            self.draw_detections(input_image, box, score, class_id)
        
        # Return the modified input image
        return input_image, detect_cls
    


    def draw_detections(self, img, box, score, class_id):
        """
        Draws bounding boxes and labels on the input image based on the detected objects.

        Args:
            img: The input image to draw detections on.
            box: Detected bounding box.
            score: Corresponding detection score.
            class_id: Class ID for the detected object.

        Returns:
            None
        """

        # Extract the coordinates of the bounding box
        x1, y1, w, h = box

        # Retrieve the color for the class ID
        color = self.color_palette[class_id]

        # Draw the bounding box on the image
        cv2.rectangle(img, (int(x1), int(y1)), (int(x1 + w), int(y1 + h)), color, 2)

        # Create the label text with class name and score
        label = f'{self.classes[class_id]}: {score:.2f}'

        # Calculate the dimensions of the label text
        (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

        # Calculate the position of the label text
        label_x = x1
        label_y = y1 - 10 if y1 - 10 > label_height else y1 + 10

        # Draw a filled rectangle as the background for the label text
        cv2.rectangle(img, (label_x, label_y - label_height), (label_x + label_width, label_y + label_height), color, cv2.FILLED)

        # Draw the label text on the image
        cv2.putText(img, label, (label_x, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)


    def main(self, img):
        # Preprocess the image data
        img_data = self.preprocess(img)

        # Run inference using the preprocessed image data
        outputs = self.session.run(None, {self.model_inputs[0].name: img_data})

        # input_image, class_id = self.postprocess(img, outputs)
        # # Perform post-processing on the outputs to obtain output image.
        # return   input_image, class_id # output image

        return self.postprocess(img, outputs)
    

if __name__ == '__main__':
    from time import time
    
    model_path = 'model/janken_detectionmodel.onnx' # モデルのパス
    test_image_filepath = 'image/ok_rock.jpg'   # テストしたい画像のパス(日本語不可！)
    output_image_filepath = 'image/res.jpg'     # 結果出力画像のパス(日本語不可！)

    args = Config(
        model=model_path,
        conf_thres=0.5,
        iou_thres=0.5)
    
    model = YOLOv8(args)

    img = cv2.imread(test_image_filepath)    # グーチョキパーのサンプル画像
    st = time()
    output_img, detect_cls = model.main(img)
    et = time()
    cv2.imwrite(output_image_filepath, output_img)    # 結果の描画してある画像
    print(detect_cls)   # 検出した手のIDリスト
    print('detect time', et - st)   # 計算時間[秒]