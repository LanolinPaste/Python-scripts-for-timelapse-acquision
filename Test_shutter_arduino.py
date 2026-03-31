import serial
import time

# Arduinoスケッチのコマンド仕様:
#   'O' または 'o' : シャッター開 (TTL HIGH)
#   'C' または 'c' : シャッター閉 (TTL LOW)
#   'S' または 's' : ステータス確認
# 応答文字列:
#   "SHUTTER_OPEN", "SHUTTER_CLOSE", "STATUS_OPEN", "STATUS_CLOSE",
#   "ERROR_UNKNOWN_COMMAND"

OPEN_CMD  = b'O'
CLOSE_CMD = b'C'
STATUS_CMD = b'S'

def connect_arduino(port, baudrate=9600):
    """Arduinoへ接続し、起動メッセージを受け取る"""
    ser = serial.Serial(
        port=port,
        baudrate=baudrate,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=2
    )
    # Arduinoはシリアル接続時にリセットされるため少し待つ
    time.sleep(2)
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    # 起動メッセージを受信して表示
    startup_msg = []
    deadline = time.time() + 3
    while time.time() < deadline:
        if ser.in_waiting > 0:
            line = ser.readline().decode('ascii', errors='replace').strip()
            if line:
                startup_msg.append(line)
        else:
            time.sleep(0.05)
    if startup_msg:
        print("  Arduino起動メッセージ:")
        for msg in startup_msg:
            print(f"    {msg}")
    return ser


def send_command(ser, cmd_bytes, label):
    """コマンドを送信し、応答を受け取って表示する。応答文字列を返す。"""
    ser.reset_input_buffer()
    ser.write(cmd_bytes)
    ser.flush()
    print(f"  送信: {label} ({cmd_bytes})")

    response = ""
    deadline = time.time() + 2
    while time.time() < deadline:
        if ser.in_waiting > 0:
            response = ser.readline().decode('ascii', errors='replace').strip()
            break
        time.sleep(0.05)

    if response:
        print(f"  応答: {response}")
    else:
        print("  応答: なし（タイムアウト）")
    return response


# ─────────────────────────────────────────────
# モード 1: 対話モード
# ─────────────────────────────────────────────
def interactive_mode(ser):
    print("\n" + "=" * 60)
    print("対話モード")
    print("=" * 60)
    print("コマンドを入力してください。")
    print("  O または o : シャッター開")
    print("  C または c : シャッター閉")
    print("  S または s : ステータス確認")
    print("  quit / exit / q : 終了")
    print()

    while True:
        try:
            cmd_str = input("コマンド> ").strip()

            if cmd_str.lower() in ('quit', 'exit', 'q'):
                print("対話モードを終了します")
                break

            if not cmd_str:
                continue

            # 1文字目をコマンドとして使用
            ch = cmd_str[0].upper()
            if ch == 'O':
                send_command(ser, OPEN_CMD,   "Open")
            elif ch == 'C':
                send_command(ser, CLOSE_CMD,  "Close")
            elif ch == 'S':
                send_command(ser, STATUS_CMD, "Status")
            else:
                # 未定義コマンドもそのまま送信（デバッグ用）
                raw = cmd_str[0].encode('ascii')
                send_command(ser, raw, f"raw '{cmd_str[0]}'")
            print()

        except KeyboardInterrupt:
            print("\n中断されました")
            break
        except Exception as e:
            print(f"エラー: {e}")


# ─────────────────────────────────────────────
# モード 2: プリセット繰り返しテスト
# ─────────────────────────────────────────────
def preset_test_mode(ser):
    print("\n" + "=" * 60)
    print("プリセットコマンドテスト（開閉を繰り返し）")
    print("=" * 60)

    repeat   = int(input("繰り返し回数 [デフォルト: 3]: ") or "3")
    open_sec = float(input("シャッター開の保持時間（秒）[デフォルト: 2.0]: ") or "2.0")
    wait_sec = float(input("シャッター閉後の待機時間（秒）[デフォルト: 1.0]: ") or "1.0")

    print(f"\nテスト開始: {repeat}回, 開:{open_sec}s, 閉後待機:{wait_sec}s")
    print("=" * 60)

    try:
        for i in range(repeat):
            print(f"\n[テスト {i+1}/{repeat}]")

            # 開
            resp = send_command(ser, OPEN_CMD, "Open")
            if "OPEN" not in resp.upper():
                print("  ⚠ 予期しない応答です")
            time.sleep(open_sec)

            # 閉
            resp = send_command(ser, CLOSE_CMD, "Close")
            if "CLOSE" not in resp.upper():
                print("  ⚠ 予期しない応答です")
            time.sleep(wait_sec)

        print("\n" + "=" * 60)
        print("テスト完了")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n中断されました")
        # 安全のためシャッターを閉じる
        print("安全のためシャッターを閉じます...")
        send_command(ser, CLOSE_CMD, "Close (safety)")
    except Exception as e:
        print(f"\nエラー: {e}")
        import traceback
        traceback.print_exc()
        send_command(ser, CLOSE_CMD, "Close (safety)")


# ─────────────────────────────────────────────
# メイン
# ─────────────────────────────────────────────
def main():
    print("=" * 60)
    print("Arduino TTL シャッターコントローラー テストツール")
    print("=" * 60)
    print()

    port     = input("COMポート [デフォルト: COM3]: ").strip() or "COM3"
    baudrate = int(input("ボーレート [デフォルト: 9600]: ").strip() or "9600")

    print(f"\n接続設定: {port}, {baudrate}bps, 8N1")

    try:
        ser = connect_arduino(port, baudrate)
        print(f"✓ {port} に接続しました\n")
    except Exception as e:
        print(f"✗ 接続エラー: {e}")
        return

    try:
        print("テストモードを選択してください:")
        print("  1: 対話モード（O/C/S コマンドを手動入力）")
        print("  2: プリセットコマンドテスト（開閉を繰り返し）")
        print()
        choice = input("選択 [1/2]: ").strip()

        if choice == '1':
            interactive_mode(ser)
        elif choice == '2':
            preset_test_mode(ser)
        else:
            print("無効な選択です")

    finally:
        # 終了時は必ずシャッターを閉じてから切断
        print("\nシャッターを閉じて切断します...")
        send_command(ser, CLOSE_CMD, "Close (shutdown)")
        ser.close()
        print(f"{port} から切断しました")


if __name__ == "__main__":
    main()
