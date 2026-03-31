import cv2
import time
from datetime import datetime
import os

def list_cameras():
    """利用可能なカメラを一覧表示"""
    print("カメラを検索中...")
    available_cameras = []
    
    for i in range(10):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                available_cameras.append(i)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                print(f"  [{i}] カメラ検出 - 解像度: {width}x{height}")
            cap.release()
    
    if not available_cameras:
        print("カメラが見つかりませんでした")
    
    return available_cameras

def get_all_camera_properties(cap):
    """カメラの全プロパティを取得して表示"""
    properties = {
        'BRIGHTNESS': cv2.CAP_PROP_BRIGHTNESS,
        'CONTRAST': cv2.CAP_PROP_CONTRAST,
        'SATURATION': cv2.CAP_PROP_SATURATION,
        'HUE': cv2.CAP_PROP_HUE,
        'GAIN': cv2.CAP_PROP_GAIN,
        'EXPOSURE': cv2.CAP_PROP_EXPOSURE,
        'AUTO_EXPOSURE': cv2.CAP_PROP_AUTO_EXPOSURE,
        'SHARPNESS': cv2.CAP_PROP_SHARPNESS,
        'AUTO_WB': cv2.CAP_PROP_AUTO_WB,
        'WB_TEMPERATURE': cv2.CAP_PROP_WB_TEMPERATURE,
        'BACKLIGHT': cv2.CAP_PROP_BACKLIGHT,
        'GAMMA': cv2.CAP_PROP_GAMMA,
    }
    
    print("\n=== カメラの対応プロパティ ===")
    for name, prop in properties.items():
        value = cap.get(prop)
        # 値が-1や0でない場合、または明示的に設定されている場合に表示
        if value != -1 or name in ['EXPOSURE', 'GAIN', 'AUTO_EXPOSURE']:
            print(f"  {name:20s}: {value}")
    print("=" * 40)

def ms_to_log_exposure(ms):
    """ミリ秒を対数スケールの露光値に変換（概算）
    多くのカメラで使われる 2^n の関係を利用
    例: -1 = 1/2秒, -5 = 1/32秒, -10 = 1/1024秒
    """
    import math
    if ms <= 0:
        return -13  # 最小値
    seconds = ms / 1000.0
    try:
        log_value = math.log2(seconds)
        return max(-13, min(-1, log_value))
    except:
        return -7  # デフォルト値

def log_to_ms_exposure(log_value):
    """対数スケールの露光値をミリ秒に変換（概算）"""
    seconds = 2 ** log_value
    return seconds * 1000

def set_camera_properties(cap, width=None, height=None, fps=None, 
                         exposure=None, gain=None, brightness=None, contrast=None):
    """カメラのプロパティを設定"""
    if width:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    if height:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    if fps:
        cap.set(cv2.CAP_PROP_FPS, fps)
    
    # 露光時間設定
    if exposure is not None:
        # 自動露出を明示的にオフ
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # manual mode
        time.sleep(0.1)
        
        success = cap.set(cv2.CAP_PROP_EXPOSURE, exposure)
        actual = cap.get(cv2.CAP_PROP_EXPOSURE)
        
        if success:
            estimated_ms = log_to_ms_exposure(actual)
            print(f"  露光時間設定: {exposure} → 実際: {actual} (約{estimated_ms:.2f}ms)")
        else:
            print(f"  警告: 露光時間の設定に失敗（現在値: {actual}）")
    
    # ゲイン設定（複数の方法を試行）
    if gain is not None:
        # 方法1: 直接設定
        success1 = cap.set(cv2.CAP_PROP_GAIN, gain)
        actual1 = cap.get(cv2.CAP_PROP_GAIN)
        
        # 方法2: ISOとして設定を試行
        success2 = cap.set(cv2.CAP_PROP_ISO_SPEED, gain)
        actual2 = cap.get(cv2.CAP_PROP_ISO_SPEED)
        
        if success1 and actual1 != -1 and actual1 != 0:
            print(f"  ゲイン設定: {gain} → 実際: {actual1}")
        elif success2 and actual2 != -1:
            print(f"  ISO感度設定: {gain} → 実際: {actual2}")
        else:
            print(f"  警告: ゲインの設定に失敗（GAIN値: {actual1}, ISO値: {actual2}）")
            print(f"       → このカメラはゲイン調整に対応していない可能性があります")
    
    # 明るさ設定（ゲインの代替）
    if brightness is not None:
        success = cap.set(cv2.CAP_PROP_BRIGHTNESS, brightness)
        actual = cap.get(cv2.CAP_PROP_BRIGHTNESS)
        if success:
            print(f"  明るさ設定: {brightness} → 実際: {actual}")
    
    # コントラスト設定
    if contrast is not None:
        success = cap.set(cv2.CAP_PROP_CONTRAST, contrast)
        actual = cap.get(cv2.CAP_PROP_CONTRAST)
        if success:
            print(f"  コントラスト設定: {contrast} → 実際: {actual}")

def show_camera_info(cap):
    """カメラの現在の設定を表示"""
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    exposure = cap.get(cv2.CAP_PROP_EXPOSURE)
    gain = cap.get(cv2.CAP_PROP_GAIN)
    auto_exposure = cap.get(cv2.CAP_PROP_AUTO_EXPOSURE)
    brightness = cap.get(cv2.CAP_PROP_BRIGHTNESS)
    
    print(f"\n現在のカメラ設定:")
    print(f"  解像度: {width}x{height}")
    print(f"  FPS: {fps}")
    print(f"  露光時間: {exposure} (約{log_to_ms_exposure(exposure):.2f}ms)")
    print(f"  ゲイン: {gain}")
    print(f"  明るさ: {brightness}")
    print(f"  自動露出: {auto_exposure}")

def capture_image(camera_id=0, save_dir="captured_images", show_preview=False, 
                 exposure=None, gain=None, brightness=None):
    """
    カメラから画像を取得して保存
    """
    try:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        print(f"\nカメラ {camera_id} を開いています...")
        cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        
        if not cap.isOpened():
            print(f"エラー: カメラ {camera_id} を開けませんでした")
            return False
        
        # 全プロパティを確認
        get_all_camera_properties(cap)
        
        # カメラパラメータを設定
        if exposure is not None or gain is not None or brightness is not None:
            print("\nカメラパラメータ設定中...")
            set_camera_properties(cap, exposure=exposure, gain=gain, brightness=brightness)
        
        # カメラ設定の表示
        show_camera_info(cap)
        
        # カメラの初期化待機
        time.sleep(1)
        
        # 画像を取得
        print("\n撮影中...")
        ret, frame = cap.read()
        
        if not ret:
            print("エラー: 画像の取得に失敗しました")
            cap.release()
            return False
        
        # ファイル名の生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(save_dir, f"capture_{timestamp}.jpg")
        
        # 画像を保存
        cv2.imwrite(filename, frame)
        print(f"画像を保存しました: {filename}")
        
        # プレビュー表示
        if show_preview:
            cv2.imshow('Captured Image', frame)
            print("\n何かキーを押すとプレビューを閉じます...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        cap.release()
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
        return False

def live_preview(camera_id=0, exposure=None, gain=None, brightness=None):
    """
    カメラのライブプレビューを表示
    ESCキーで終了
    """
    print(f"\nカメラ {camera_id} のライブプレビューを開始します")
    print("ESC: 終了 | SPACE: 撮影")
    print("+/-: 露光調整 | [/]: ゲイン調整 | 9/0: 明るさ調整")
    
    cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print(f"エラー: カメラ {camera_id} を開けませんでした")
        return
    
    # 初期パラメータ設定
    if exposure is not None or gain is not None or brightness is not None:
        print("\nカメラパラメータ設定中...")
        set_camera_properties(cap, exposure=exposure, gain=gain, brightness=brightness)
    
    get_all_camera_properties(cap)
    show_camera_info(cap)
    
    # 現在の設定値を取得
    current_exposure = cap.get(cv2.CAP_PROP_EXPOSURE)
    current_gain = cap.get(cv2.CAP_PROP_GAIN)
    current_brightness = cap.get(cv2.CAP_PROP_BRIGHTNESS)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("エラー: フレームの取得に失敗しました")
            break
        
        # 現在の設定を画面に表示
        exposure_ms = log_to_ms_exposure(current_exposure)
        info_text = f"Exp: {current_exposure:.1f} ({exposure_ms:.1f}ms) | Gain: {current_gain:.0f} | Bright: {current_brightness:.0f}"
        cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.7, (0, 255, 0), 2)
        
        cv2.imshow('Live Preview', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == 32:  # SPACE
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"captured_images/capture_{timestamp}.jpg"
            os.makedirs("captured_images", exist_ok=True)
            cv2.imwrite(filename, frame)
            print(f"撮影: {filename}")
        elif key == ord('+') or key == ord('='):
            current_exposure += 1
            cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
            cap.set(cv2.CAP_PROP_EXPOSURE, current_exposure)
            current_exposure = cap.get(cv2.CAP_PROP_EXPOSURE)
            print(f"露光: {current_exposure:.1f} ({log_to_ms_exposure(current_exposure):.1f}ms)")
        elif key == ord('-'):
            current_exposure -= 1
            cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
            cap.set(cv2.CAP_PROP_EXPOSURE, current_exposure)
            current_exposure = cap.get(cv2.CAP_PROP_EXPOSURE)
            print(f"露光: {current_exposure:.1f} ({log_to_ms_exposure(current_exposure):.1f}ms)")
        elif key == ord(']'):
            current_gain += 5
            cap.set(cv2.CAP_PROP_GAIN, current_gain)
            current_gain = cap.get(cv2.CAP_PROP_GAIN)
            print(f"ゲイン: {current_gain:.0f}")
        elif key == ord('['):
            current_gain -= 5
            cap.set(cv2.CAP_PROP_GAIN, current_gain)
            current_gain = cap.get(cv2.CAP_PROP_GAIN)
            print(f"ゲイン: {current_gain:.0f}")
        elif key == ord('0'):
            current_brightness += 5
            cap.set(cv2.CAP_PROP_BRIGHTNESS, current_brightness)
            current_brightness = cap.get(cv2.CAP_PROP_BRIGHTNESS)
            print(f"明るさ: {current_brightness:.0f}")
        elif key == ord('9'):
            current_brightness -= 5
            cap.set(cv2.CAP_PROP_BRIGHTNESS, current_brightness)
            current_brightness = cap.get(cv2.CAP_PROP_BRIGHTNESS)
            print(f"明るさ: {current_brightness:.0f}")
    
    cap.release()
    cv2.destroyAllWindows()

def main():
    """メインプログラム"""
    print("=" * 50)
    print("USBカメラ撮影プログラム (露光時間改善版)")
    print("=" * 50)
    print()
    
    cameras = list_cameras()
    if not cameras:
        return
    
    print()
    
    # カメラ選択
    if len(cameras) > 1:
        try:
            idx = int(input(f"使用するカメラの番号 [{cameras}]: "))
            if idx not in cameras:
                idx = cameras[0]
        except:
            idx = cameras[0]
    else:
        idx = cameras[0]
    
    print()
    print("カメラパラメータ設定（空Enter でスキップ）:")
    print("  露光時間: -13～-1 の対数値 (例: -7 で約7.8ms)")
    print("            または m を付けてミリ秒指定 (例: 10m で10ms)")
    
    exposure_input = input("露光時間 [-13～-1 または Xm]: ")
    gain_input = input("ゲイン [0～100]: ")
    brightness_input = input("明るさ [0～255、ゲインの代替]: ")
    
    # 露光時間の処理
    exposure = None
    if exposure_input:
        if exposure_input.endswith('m'):
            # ミリ秒指定
            ms = float(exposure_input[:-1])
            exposure = ms_to_log_exposure(ms)
            print(f"  → {ms}ms を対数値 {exposure:.2f} に変換")
        else:
            exposure = float(exposure_input)
    
    gain = float(gain_input) if gain_input else None
    brightness = float(brightness_input) if brightness_input else None
    
    print()
    print("モード選択:")
    print("  1: 1枚撮影（プレビューあり）")
    print("  2: 1枚撮影（プレビューなし）")
    print("  3: ライブプレビュー（リアルタイム調整）")
    
    try:
        mode = int(input("モード [1-3]: "))
    except:
        mode = 1
    
    print()
    
    # 実行
    if mode == 1:
        success = capture_image(camera_id=idx, show_preview=True, 
                              exposure=exposure, gain=gain, brightness=brightness)
    elif mode == 2:
        success = capture_image(camera_id=idx, show_preview=False, 
                              exposure=exposure, gain=gain, brightness=brightness)
    elif mode == 3:
        live_preview(camera_id=idx, exposure=exposure, gain=gain, brightness=brightness)
        success = True
    else:
        print("無効なモードです")
        success = False
    
    if success and mode in [1, 2]:
        print("\nテスト撮影が完了しました！")

if __name__ == "__main__":
    main()
