import sys
import time
import firebase_admin
from firebase_admin import credentials, firestore, db  # db 모듈 추가
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QGridLayout
from datetime import datetime
import RPi.GPIO as GPIO  # Raspberry Pi GPIO 라이브러리 추가

# 서보 모터 핀 설정 (예: GPIO 17)
SERVO_PIN = 17


# Firestore 및 Realtime Database 초기화
cred = credentials.Certificate("hackathon-2024-a0eed-firebase-adminsdk-lcn9w-ec4b146ffb.json")  # serviceAccount.json 경로로 변경
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://hackathon-2024-a0eed-default-rtdb.firebaseio.com/'  # Realtime Database URL 입력
})

db_firestore = firestore.client()  # Firestore 클라이언트
db_realtime = db  # Realtime Database 클라이언트

SERVO_PIN = 18  # 사용할 GPIO 핀 번호

# GPIO 초기 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# 서보 모터 PWM 설정
servo_pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz
servo_pwm.start(0)

def move_servo(angle):
    """서보 모터를 특정 각도로 이동하는 함수."""
    duty = angle / 18 + 2  # 각도를 듀티 사이클로 변환
    GPIO.output(SERVO_PIN, True)
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(SERVO_PIN, False)
    servo_pwm.ChangeDutyCycle(0)

selected_time = None

class GreetingScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(480, 800)
        self.setStyleSheet("background-color: #FFFFFF;")
        label_top = QLabel("주차를 간편하게", self)
        label_top.setStyleSheet("font-size: 20px; color: #555555; font-weight: bold; font-family: Arial;text-align: center;")
        label_top.setAlignment(Qt.AlignCenter)

        label_main = QLabel("안녕하세요!", self)
        label_main.setStyleSheet("font-size: 50px; color: #b22222; font-weight: bold; font-family: 'NanumGothic', '맑은 고딕';text-align: center;")
        label_main.setAlignment(Qt.AlignCenter)

        icon_label = QLabel(self)
        icon_pixmap = QPixmap("touch_icon.png").scaled(100, 100, Qt.KeepAspectRatio)
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap)

        button_touch = QPushButton("화면을 터치해 주세요", self)
        button_touch.setStyleSheet(
            "font-size: 24px; font-weight: bold; color:  #b22222; background-color: #FFD700; padding: 15px; border-radius: 10px; font-family: 'NanumGothic', '맑은 고딕';"
        )
        button_touch.clicked.connect(self.on_touch)
        button_touch.setFixedWidth(300)

        button_layout = QHBoxLayout()
        button_layout.addWidget(icon_label)
        button_layout.addWidget(button_touch)
        button_layout.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(label_top)
        layout.addWidget(label_main)
        layout.addLayout(button_layout)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        self.setLayout(layout)

    def on_touch(self, event):
        self.next_screen = NextScreen()
        self.next_screen.show()
        self.hide()

    def mousePressEvent(self, event):
        self.next_screen = NextScreen()
        self.next_screen.show()
        self.hide()

class NextScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(480, 800)
        self.setStyleSheet("background-color: #FFFFFF;")
        label = QLabel("이용 시간을 선택해 주세요.", self)
        label.setStyleSheet("font-size: 24px; color: #555555; font-weight: bold; font-family: Arial;")
        label.setAlignment(Qt.AlignCenter)

        button_style = """
            QPushButton {
                font-size: 18px;
                font-family: 'NanumGothic';
                color: #555555;
                background-color: #E0F7FA;
                border-radius: 15px;
                padding: 20px;
            }
            QPushButton:hover {
                background-color: #B2EBF2;
            }
        """
        
        self.buttons = {
            "30분 이하": 30,
            "60분 이하": 60,
            "120분 이하": 120,
            "120분 이상": 150,
        }
        
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addSpacing(20)

        button_layout = QGridLayout()
        row, col = 0, 0
        for text, time in self.buttons.items():
            button = QPushButton(text)
            button.setStyleSheet(button_style)
            button.setFixedSize(180, 80)
            button.clicked.connect(lambda checked, time=time: self.select_time(time))
            button_layout.addWidget(button, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

        layout.addLayout(button_layout)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(30, 30, 30, 30)

        self.setLayout(layout)

    def select_time(self, time):
        global selected_time
        selected_time = time
        self.next_screen = SeatSelectionScreen()
        self.next_screen.show()
        self.hide()

class SeatSelectionScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(480, 800)
        self.setStyleSheet("background-color: #FFFFFF;")
        label = QLabel("자리를 선택해주세요.", self)
        label.setStyleSheet("font-size: 24px; color: #555555; font-weight: bold; font-family: Arial;")
        label.setAlignment(Qt.AlignCenter)

        self.default_button_style = """
            QPushButton {
                font-size: 18px;
                font-family: 'NanumGothic';
                color: #FFFFFF;
                background-color: #4CAF50;
                border-radius: 10px;
                padding: 30px;
            }
        """
        self.occupied_button_style = """
            QPushButton {
                font-size: 18px;
                font-family: 'NanumGothic';
                color: #FFFFFF;
                background-color: #FF0000;
                border-radius: 10px;
                padding: 30px;
            }
        """

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addSpacing(20)

        self.button_layout = QGridLayout()
        
        self.seat_buttons = {}
        for i in range(4):
            for j in range(2):
                seat_num = j + i * 2 + 1
                button = QPushButton(f"{seat_num}")
                button.setFixedSize(150, 100)
                button.clicked.connect(lambda checked, seat_num=seat_num: self.select_seat(seat_num))
                self.button_layout.addWidget(button, i, j)
                self.seat_buttons[seat_num] = button

        layout.addLayout(self.button_layout)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(30, 30, 30, 30)

        self.setLayout(layout)
        self.load_seat_status()

    def load_seat_status(self):
        global selected_time
        recommendation_index = {30: 0, 60: 1, 120: 2, 150: 3}.get(selected_time, -1)

        for seat_num, button in self.seat_buttons.items():
            seat_doc = db_firestore.collection("Seat").document(f"Seat{seat_num}")
            seat_data = seat_doc.get()
            if seat_data.exists and seat_data.to_dict().get("Status") == True:
                button.setStyleSheet(self.occupied_button_style)
                button.setEnabled(False)
            else:
                button.setStyleSheet(self.default_button_style)
                button.setEnabled(True)

                row_index = (seat_num - 1) // 2
                if row_index == recommendation_index:
                    button.setText(f"{seat_num} (추천)")
                else:
                    button.setText(f"{seat_num}")

    def select_seat(self, seat_num):
        # Realtime Database에서 CarNumber 가져오기
        car_number = self.get_car_number_from_realtime_db()

        current_time = datetime.now().strftime("%Y%m%d%H%M")

        # Firestore에 Seat 문서 업데이트
        seat_ref = db_firestore.collection("Seat").document(f"Seat{seat_num}")
        seat_ref.update({
            "Status": True,
            "CarNumber": car_number,
            "Time": current_time # 현재 서버 시간을 저장
        })

        db_realtime.reference(f'Seat/Seat{seat_num}').update({
        "Status": True
        })

        # 주차를 시작하겠습니다 페이지로 넘어가기
        self.next_screen = ParkingStartScreen()  # 주차 시작 화면으로 전환
        self.next_screen.show()
        self.hide()

    def get_car_number_from_realtime_db(self):
        # Realtime Database에서 CarNumber를 가져오는 로직
        ref = db_realtime.reference('EntryCam')  # EntryCam 경로의 참조
        car_number_data = ref.child('CarNumber').get()  # CarNumber 데이터 가져오기
        return car_number_data  # 실제 CarNumber 반환

class ParkingStartScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(480, 800)
        self.setStyleSheet("background-color: #FFFFFF;")
        label = QLabel("주차를 시작하겠습니다!", self)
        label.setStyleSheet("font-size: 30px; color: #555555; font-weight: bold; font-family: Arial;")
        label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.setAlignment(Qt.AlignCenter)

        self.setLayout(layout)

        # 서보 모터를 올리고 5초 후에 내리는 동작 수행
        move_servo(90)  # 서보 모터를 올리는 위치 (예: 90도)
        QTimer.singleShot(5000, self.lower_servo_and_return)  # 5초 후에 모터 내리고 초기 화면으로 돌아감

    def lower_servo_and_return(self):
        move_servo(0)  # 서보 모터를 내리는 위치 (예: 0도)
        self.return_to_greeting_screen()

    def return_to_greeting_screen(self):
        servo_pwm.stop()  # PWM 종료
        GPIO.cleanup()  # GPIO 정리
        self.close()  # 현재 창 닫기
        self.greeting_screen = GreetingScreen()
        self.greeting_screen.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    greeting_screen = GreetingScreen()
    greeting_screen.show()
    sys.exit(app.exec_())