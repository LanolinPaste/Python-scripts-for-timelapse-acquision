/*
 * Arduino シャッターコントローラー制御プログラム
 * 
 * 接続:
 * - デジタルピン2: シャッターコントローラーのTTL信号入力に接続
 * - GND: シャッターコントローラーのGNDに接続
 * 
 * シリアルコマンド:
 * 'O' または 'o' : シャッター開 (TTL HIGH)
 * 'C' または 'c' : シャッター閉 (TTL LOW)
 * 'S' または 's' : ステータス確認
 */

const int SHUTTER_PIN = 2;  // シャッター制御用ピン
bool shutterState = false;   // 現在のシャッター状態 (false=閉, true=開)

void setup() {
  // シリアル通信を初期化
  Serial.begin(9600);
  
  // シャッター制御ピンを出力に設定
  pinMode(SHUTTER_PIN, OUTPUT);
  digitalWrite(SHUTTER_PIN, LOW);  // 初期状態は閉
  
  // 起動メッセージ
  Serial.println("Arduino Shutter Controller Ready");
  Serial.println("Commands: O=Open, C=Close, S=Status");
}

void loop() {
  // シリアルデータが来たら処理
  if (Serial.available() > 0) {
    char command = Serial.read();
    
    switch (command) {
      case 'O':
      case 'o':
        // シャッター開
        digitalWrite(SHUTTER_PIN, HIGH);
        shutterState = true;
        Serial.println("SHUTTER_OPEN");
        break;
        
      case 'C':
      case 'c':
        // シャッター閉
        digitalWrite(SHUTTER_PIN, LOW);
        shutterState = false;
        Serial.println("SHUTTER_CLOSE");
        break;
        
      case 'S':
      case 's':
        // ステータス確認
        if (shutterState) {
          Serial.println("STATUS_OPEN");
        } else {
          Serial.println("STATUS_CLOSE");
        }
        break;
        
      default:
        // 不明なコマンド
        Serial.println("ERROR_UNKNOWN_COMMAND");
        break;
    }
  }
}