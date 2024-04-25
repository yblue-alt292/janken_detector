import cv2

from janken_functions import *
from model_prediction import Config, YOLOv8


model_path = 'model/janken_detectionmodel.onnx' # モデルのパス
test_image_filepath = 'image/ok_rock.jpg'   # テストしたい画像のパス(日本語不可！)
output_image_filepath = 'image/res.jpg'     # 結果出力画像のパス(日本語不可！)



if __name__ == "__main__":
    # モデルの定義
    args = Config(
    model=model_path,
    conf_thres=0.5,
    iou_thres=0.5)

    model = YOLOv8(args)
    
    img = cv2.imread(test_image_filepath)    # 推論したい画像を読み込み
    output_img, ID_player_hands = model.main(img)    # モデルで推論
    cv2.imwrite(output_image_filepath, output_img)    # 結果の描画してある画像の保存
    
    ID_com_hand = gen_com_hand()    # ランダムにPCの手を生成
    winner = janken(ID_player_hands, ID_com_hand)   # プレイヤーの手と比較して勝敗決定
    
    # 結果出力
    print(f'COM hand: {hands_dic[ID_com_hand]}')
    print(f'PLAYER hands:{[hands_dic[ID] for ID in ID_player_hands]}')
    print(f'winner:{winner}')
    
    