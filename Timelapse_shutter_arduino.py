import cv2
import serial
import time
from datetime import datetime
import os

class ShutterController:
    """Arduinoシャッターコントローラークラス"""
    
    def __init__(self, port='COM3', baudrate=9600):
        """
        Parameters:
        - port: ArduinoのCOMポート (例: 'COM3', '/dev/ttyUSB0')
        - baudrate: 通信速度
        """
        self.ser = None
        self.port = port
        self.baudrate = baudrate
        
    def connect(self):
        """Arduinoに接続"""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Arduino起動待ち
            
            # 起動メッセージを読み取り
            if self.ser.in_waiting:
                msg = self.ser.readline().decode().strip()
                print(f"Arduino: {msg}")
            
            print(f"Arduino接続成功: {self.port}")
            return True
        except Exception as e:
            print(f"Arduino接続エラー: {e}")
            return False
    
    def open_shutter(self):
        """シャッターを開く"""
        if self.ser:
            self.ser.write(b'O')
            time.sleep(0.1)
            response = self.ser.readline().decode().strip()
            print(f"  シャッター: 開 ({response})")
            return response == "SHUTTER_OPEN"
        return False
    
    def close_shutter(self):
        """シャッターを閉じる"""
        if self.ser:
            self.ser.write(b'C')
            time.sleep(0.1)
            response = self.ser.readline().decode().strip()
            print(f"  シャッター: 閉 ({response})")
            return response == "SHUTTER_CLOSE"
        return False
    
    def get_status(self):
        """シャッター状態を取得"""
        if self.ser:
            self.ser.write(b'S')
            time.sleep(0.1)
            response = self.ser.readline().decode().strip()
            return response
        return None
    
    def disconnect(self):
        """接続を切断"""
        if self.ser:
            self.close_shutter()  # 念のため閉じる
            self.ser.close()
            print("Arduino接続を切断しました")

class TimelapseCamera:
    """タイムラプスカメラクラス"""
    
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.cap = None
        
    def open(self):
        """カメラを開く"""
        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
        if self.cap.isOpened():
            print(f"カメラ {self.camera_id} を開きました")
            time.sleep(1)  # 初期化待ち
            return True
        else:
            print(f"カメラ {self.camera_id} を開けませんでした")
            return False
    
    def set_exposure(self, exposure_value):
        """
        露光時間を設定
        
        Parameters:
        - exposure_value: 露光時間（カメラ依存、通常は-13～-1で対数スケール、
                         または直接ミリ秒単位の値）
        
        Returns:
        - 設定成功したかどうか
        """
        if not self.cap or not self.cap.isOpened():
            print("エラー: カメラが開かれていません")
            return False
        
        # 自動露出をオフにする
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # 0.25 = manual mode
        time.sleep(0.1)
        
        # 露光時間を設定
        success = self.cap.set(cv2.CAP_PROP_EXPOSURE, exposure_value)
        
        if success:
            actual_value = self.cap.get(cv2.CAP_PROP_EXPOSURE)
            print(f"  露光時間設定: {exposure_value} → 実際の値: {actual_value}")
            return True
        else:
            print(f"  警告: 露光時間の設定に失敗しました")
            return False
    
    def set_gain(self, gain_value):
        """
        ゲインを設定
        
        Parameters:
        - gain_value: ゲイン値（カメラ依存、通常は0～100程度）
        
        Returns:
        - 設定成功したかどうか
        """
        if not self.cap or not self.cap.isOpened():
            print("エラー: カメラが開かれていません")
            return False
        
        # ゲインを設定
        success = self.cap.set(cv2.CAP_PROP_GAIN, gain_value)
        
        if success:
            actual_value = self.cap.get(cv2.CAP_PROP_GAIN)
            print(f"  ゲイン設定: {gain_value} → 実際の値: {actual_value}")
            return True
        else:
            print(f"  警告: ゲインの設定に失敗しました")
            return False
    
    def set_brightness(self, brightness_value):
        """
        明るさを設定（ゲインの代替）
        
        Parameters:
        - brightness_value: 明るさ値（カメラ依存、通常は0～255程度）
        
        Returns:
        - 設定成功したかどうか
        """
        if not self.cap or not self.cap.isOpened():
            print("エラー: カメラが開かれていません")
            return False
        
        # 明るさを設定
        success = self.cap.set(cv2.CAP_PROP_BRIGHTNESS, brightness_value)
        
        if success:
            actual_value = self.cap.get(cv2.CAP_PROP_BRIGHTNESS)
            print(f"  明るさ設定: {brightness_value} → 実際の値: {actual_value}")
            return True
        else:
            print(f"  警告: 明るさの設定に失敗しました")
            return False
    
    def get_current_settings(self):
        """現在のカメラ設定を取得して表示"""
        if not self.cap or not self.cap.isOpened():
            return
        
        exposure = self.cap.get(cv2.CAP_PROP_EXPOSURE)
        gain = self.cap.get(cv2.CAP_PROP_GAIN)
        brightness = self.cap.get(cv2.CAP_PROP_BRIGHTNESS)
        auto_exposure = self.cap.get(cv2.CAP_PROP_AUTO_EXPOSURE)
        
        print("\n現在のカメラ設定:")
        print(f"  露光時間: {exposure}")
        print(f"  ゲイン: {gain}")
        print(f"  明るさ: {brightness}")
        print(f"  自動露出: {auto_exposure}")
        
        return {
            "exposure": exposure, 
            "gain": gain, 
            "brightness": brightness,
            "auto_exposure": auto_exposure
        }
    
    def capture(self, filename):
        """画像を撮影して保存"""
        if not self.cap or not self.cap.isOpened():
            print("エラー: カメラが開かれていません")
            return False
        
        ret, frame = self.cap.read()
        if ret:
            cv2.imwrite(filename, frame)
            return True
        else:
            print("エラー: 画像取得失敗")
            return False
    
    def close(self):
        """カメラを閉じる"""
        if self.cap:
            self.cap.release()
            print("カメラを閉じました")

def timelapse_capture(camera_id, arduino_port, num_frames, interval, 
                     shutter_open_delay=0.5, shutter_close_delay=0.2,
                     save_dir="timelapse", exposure=None, gain=None, brightness=None):
    """
    タイムラプス撮影を実行
    
    Parameters:
    - camera_id: カメラID
    - arduino_port: ArduinoのCOMポート
    - num_frames: 撮影枚数
    - interval: 撮影間隔（秒）
    - shutter_open_delay: シャッター開後の待機時間（秒）
    - shutter_close_delay: 撮影後、シャッター閉までの待機時間（秒）
    - save_dir: 保存先ディレクトリ
    - exposure: 露光時間（Noneの場合は設定しない）
    - gain: ゲイン（Noneの場合は設定しない）
    - brightness: 明るさ（Noneの場合は設定しない）
    """
    
    # 保存先ディレクトリの作成
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # 初期化
    shutter = ShutterController(port=arduino_port)
    camera = TimelapseCamera(camera_id=camera_id)
    
    try:
        # Arduino接続
        if not shutter.connect():
            print("Arduino接続に失敗しました")
            return False
        
        # カメラオープン
        if not camera.open():
            print("カメラオープンに失敗しました")
            shutter.disconnect()
            return False
        
        # カメラパラメータ設定
        print("\nカメラパラメータ設定中...")
        if exposure is not None:
            camera.set_exposure(exposure)
        if gain is not None:
            camera.set_gain(gain)
        if brightness is not None:
            camera.set_brightness(brightness)
        
        # 現在の設定を表示
        camera.get_current_settings()
        
        print("\n" + "="*50)
        print(f"タイムラプス撮影開始")
        print(f"  撮影枚数: {num_frames}枚")
        print(f"  撮影間隔: {interval}秒")
        print(f"  保存先: {save_dir}/")
        if exposure is not None:
            print(f"  露光時間: {exposure}")
        if gain is not None:
            print(f"  ゲイン: {gain}")
        if brightness is not None:
            print(f"  明るさ: {brightness}")
        print("="*50 + "\n")
        
        # タイムラプス撮影ループ
        for i in range(num_frames):
            print(f"\n[{i+1}/{num_frames}] 撮影中...")
            
            # 1. シャッターを開く
            shutter.open_shutter()
            time.sleep(shutter_open_delay)  # シャッター開動作の完了待ち
            
            # 2. 撮影
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(save_dir, f"frame_{i+1:04d}_{timestamp}.jpg")
            
            if camera.capture(filename):
                print(f"  保存: {filename}")
            else:
                print(f"  エラー: 撮影失敗")
            
            time.sleep(shutter_close_delay)
            
            # 3. シャッターを閉じる
            shutter.close_shutter()
            
            # 4. 次の撮影までの待機（最後の撮影では待機しない）
            if i < num_frames - 1:
                print(f"  次の撮影まで {interval}秒待機...")
                time.sleep(interval)
        
        print("\n" + "="*50)
        print("タイムラプス撮影完了！")
        print("="*50)
        
        return True
        
    except KeyboardInterrupt:
        print("\n\nユーザーによって中断されました")
        return False
        
    except Exception as e:
        print(f"\nエラー: {e}")
        return False
        
    finally:
        # クリーンアップ
        camera.close()
        shutter.disconnect()
        cv2.destroyAllWindows()

def main():
    """メイン関数"""
    print("=" * 60)
    print("タイムラプス撮影システム (Arduino連携)")
    print("=" * 60)
    print()
    
    # 設定入力
    try:
        camera_id = int(input("カメラID [デフォルト: 0]: ") or "0")
        arduino_port = input("ArduinoのCOMポート [デフォルト: COM3]: ") or "COM3"
        num_frames = int(input("撮影枚数 [デフォルト: 10]: ") or "10")
        interval = float(input("撮影間隔（秒） [デフォルト: 5.0]: ") or "5.0")
        
        # カメラパラメータ設定
        print("\nカメラパラメータ設定（空Enter でスキップ）:")
        exposure_input = input("露光時間 [通常は-13～-1、空Enter=自動]: ")
        gain_input = input("ゲイン [通常は0～100、空Enter=自動]: ")
        brightness_input = input("明るさ [通常は0～255、空Enter=自動]: ")
        
        exposure = float(exposure_input) if exposure_input else None
        gain = float(gain_input) if gain_input else None
        brightness = float(brightness_input) if brightness_input else None
        
        print("\n設定確認:")
        print(f"  カメラID: {camera_id}")
        print(f"  Arduinoポート: {arduino_port}")
        print(f"  撮影枚数: {num_frames}枚")
        print(f"  撮影間隔: {interval}秒")
        print(f"  露光時間: {exposure if exposure is not None else '自動'}")
        print(f"  ゲイン: {gain if gain is not None else '自動'}")
        print(f"  明るさ: {brightness if brightness is not None else '自動'}")
        print(f"  予想所要時間: 約{num_frames * interval / 60:.1f}分")
        
        input("\nEnterキーを押すと撮影を開始します...")
        
        # タイムラプス撮影実行
        timelapse_capture(
            camera_id=camera_id,
            arduino_port=arduino_port,
            num_frames=num_frames,
            interval=interval,
            exposure=exposure,
            gain=gain,
            brightness=brightness
        )
        
    except ValueError:
        print("エラー: 無効な入力です")
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    main()