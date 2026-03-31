import serial
import time

def test_shutter_communication():
    """
    シャッターコントローラーとのRS232C通信をテストする簡易スクリプト
    """
    print("=" * 60)
    print("シャッターコントローラー 通信テストツール")
    print("=" * 60)
    print()
    
    # 設定入力
    port = input("COMポート [デフォルト: COM3]: ") or "COM3"
    baudrate = int(input("ボーレート [デフォルト: 9600]: ") or "9600")
    
    print(f"\n接続設定:")
    print(f"  ポート: {port}")
    print(f"  ボーレート: {baudrate}")
    print(f"  データビット: 8")
    print(f"  パリティ: None")
    print(f"  ストップビット: 1")
    print()
    
    # シリアルポート接続
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        print(f"✓ {port} に接続しました")
        time.sleep(0.5)
        
        # バッファクリア
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
    except Exception as e:
        print(f"✗ 接続エラー: {e}")
        return
    
    # 対話モード
    print("\n" + "=" * 60)
    print("対話モード")
    print("=" * 60)
    print("コマンドを入力してください。")
    print("  - 文字列をそのまま送信: 例) open")
    print("  - 16進数で送信: 例) hex:4F50454E  (OPENのASCII)")
    print("  - 終了: quit または exit")
    print()
    
    # コマンド例を表示
    print("よく使われるコマンド例:")
    print("  open\\r\\n    : 'open' + CR+LF")
    print("  close\\r\\n   : 'close' + CR+LF")
    print("  open\\r      : 'open' + CR")
    print("  O           : 1文字コマンド 'O'")
    print("  C           : 1文字コマンド 'C'")
    print()
    
    while True:
        try:
            # コマンド入力
            command_str = input("コマンド> ").strip()
            
            if command_str.lower() in ['quit', 'exit', 'q']:
                print("終了します")
                break
            
            if not command_str:
                continue
            
            # コマンドをバイト列に変換
            if command_str.startswith('hex:'):
                # 16進数モード
                hex_str = command_str[4:].replace(' ', '')
                try:
                    command_bytes = bytes.fromhex(hex_str)
                    print(f"送信(16進): {hex_str}")
                except ValueError:
                    print("エラー: 無効な16進数です")
                    continue
            else:
                # テキストモード
                # エスケープシーケンスを処理
                command_str = command_str.replace('\\r', '\r')
                command_str = command_str.replace('\\n', '\n')
                command_str = command_str.replace('\\t', '\t')
                command_bytes = command_str.encode('ascii')
                
                # 送信内容を表示（改行文字を可視化）
                display_str = command_str.replace('\r', '\\r').replace('\n', '\\n')
                print(f"送信: '{display_str}'")
            
            # バッファクリア
            ser.reset_input_buffer()
            
            # コマンド送信
            ser.write(command_bytes)
            ser.flush()
            print(f"  → {len(command_bytes)} バイト送信")
            
            # 応答待ち
            time.sleep(0.2)
            
            # 応答受信
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting)
                
                # ASCII解釈可能な場合は文字列表示
                try:
                    response_str = response.decode('ascii')
                    # 改行文字を可視化
                    display_response = response_str.replace('\r', '\\r').replace('\n', '\\n')
                    print(f"応答(ASCII): '{display_response}'")
                except:
                    print(f"応答(RAW): {response}")
                
                # 16進数表示
                hex_response = ' '.join([f'{b:02X}' for b in response])
                print(f"応答(16進): {hex_response}")
            else:
                print("応答: なし")
            
            print()
            
        except KeyboardInterrupt:
            print("\n\n中断されました")
            break
        except Exception as e:
            print(f"エラー: {e}")
            import traceback
            traceback.print_exc()
    
    # 切断
    ser.close()
    print(f"\n{port} から切断しました")

def preset_command_test():
    """
    プリセットコマンドでテストする
    """
    print("=" * 60)
    print("シャッターコントローラー プリセットコマンドテスト")
    print("=" * 60)
    print()
    
    # 設定入力
    port = input("COMポート [デフォルト: COM3]: ") or "COM3"
    baudrate = int(input("ボーレート [デフォルト: 9600]: ") or "9600")
    
    print("\nシャッター開コマンドを入力してください:")
    print("  例) open\\r\\n, O, @, ens\\r など")
    open_cmd_str = input("開コマンド> ")
    
    print("\nシャッター閉コマンドを入力してください:")
    print("  例) close\\r\\n, C, A, dis\\r など")
    close_cmd_str = input("閉コマンド> ")
    
    # エスケープシーケンス処理
    open_cmd_str = open_cmd_str.replace('\\r', '\r').replace('\\n', '\n')
    close_cmd_str = close_cmd_str.replace('\\r', '\r').replace('\\n', '\n')
    
    open_cmd = open_cmd_str.encode('ascii')
    close_cmd = close_cmd_str.encode('ascii')
    
    # シリアルポート接続
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        print(f"\n✓ {port} に接続しました")
        time.sleep(0.5)
        
    except Exception as e:
        print(f"\n✗ 接続エラー: {e}")
        return
    
    # テストループ
    print("\n" + "=" * 60)
    print("テスト実行中...")
    print("=" * 60)
    
    try:
        for i in range(3):
            print(f"\n[テスト {i+1}/3]")
            
            # シャッター開
            print("  シャッター開コマンド送信...")
            ser.reset_input_buffer()
            ser.write(open_cmd)
            ser.flush()
            time.sleep(0.2)
            
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting)
                print(f"    応答: {response}")
            else:
                print("    応答: なし")
            
            time.sleep(2)
            
            # シャッター閉
            print("  シャッター閉コマンド送信...")
            ser.reset_input_buffer()
            ser.write(close_cmd)
            ser.flush()
            time.sleep(0.2)
            
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting)
                print(f"    応答: {response}")
            else:
                print("    応答: なし")
            
            time.sleep(1)
        
        print("\n" + "=" * 60)
        print("テスト完了")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n中断されました")
    except Exception as e:
        print(f"\nエラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ser.close()
        print(f"\n{port} から切断しました")

def main():
    """メイン関数"""
    print()
    print("テストモードを選択してください:")
    print("  1: 対話モード（自由にコマンド入力）")
    print("  2: プリセットコマンドテスト（開閉を繰り返し）")
    print()
    
    choice = input("選択 [1/2]: ").strip()
    
    if choice == '1':
        test_shutter_communication()
    elif choice == '2':
        preset_command_test()
    else:
        print("無効な選択です")

if __name__ == "__main__":
    main()
