import customtkinter as ctk
import serial
import threading
import time
import serial.tools.list_ports

# シリアルポート
serial_port = None

Serial_Opened = 0

# シリアルポートを開く関数
def open_serial_port():
    global serial_port
    if serial_port and serial_port.is_open:
        printf.insert("end","Already opened the port.\n")
        return
    try:
        serial_port = serial.Serial(com_port_var.get(), baud_rate_var.get(), timeout=1)
        comment = com_port_var.get() + " is opened.\n"
        printf.insert("end",comment)
        start_monitoring_thread()
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")

# シリアルポートを閉じる関数
def close_serial_port(event=None):
    global serial_port
    if serial_port and serial_port.is_open:
        serial_port.close()
        printf.insert("end","Successfully closed the port.\n")
    else:
        printf.insert("end","COM port is already closed.\n")

def destroy_application(event=None):
    close_serial_port()
    app.destroy()

# データを送信する関数
def send_serial_data(event=None):
    global serial_port
    if serial_port and serial_port.is_open:
        data_to_send = send_data_var.get()

        # 送信データをバイト配列としてエンコード
        encoded_data = data_to_send.encode()
       
        if len(encoded_data) < 149:
            encoded_data += b'\x00' * (149 - len(encoded_data)) # 150byteに足りない部分を0埋め
        for byte in encoded_data:
            serial_port.write(bytes([byte]))
        #serial_port.write(encoded_data)
        send_data_var.set("")
    else:
        data = "COM port is not open yet.\n"
        printf.insert("end",data)
        printf.see("end")

# シリアルポートをモニタリングする関数
def monitor_serial_data():
    global serial_port
    while True:
        try:
            if serial_port and serial_port.is_open:
                data = serial_port.read_all()
                if data:
                    app.after(0, update_received_data, data)
            else:
                break
        except serial.SerialException as e:
            print(f"Serial error: {e}")
            break
        except Exception as e:
            print(f"Other error: {e}")
            break
        time.sleep(0.1)


# 受信データのアップデート
def update_received_data(data):
    #受信データを16進数形式で表示
    received_data_var.set(data.hex())
    received_data_display.insert("end",data)
    received_data_display.see("end")

# シリアルデータ監視スレッドを開始
def start_monitoring_thread():
    monitoring_thread = threading.Thread(target=monitor_serial_data, daemon=True)
    monitoring_thread.start()


# シリアルポート検索
def get_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

app = ctk.CTk()

# シリアルポート設定用変数
baud_rate_var = ctk.StringVar(value="115200")

# 送信データ用変数
send_data_var = ctk.StringVar()

# 受信データ表示用変数
received_data_var = ctk.StringVar()

# COMポートのドロップダウンリスト
com_port_var = ctk.StringVar()
com_ports = get_serial_ports()
if not com_ports:
    com_ports = ["No Ports Available"]
com_port_dropdown = ctk.CTkOptionMenu(app, variable=com_port_var, values=com_ports)
com_port_dropdown.grid(row=0, column=0, padx=0, pady=0)

# ボーレートのドロップダウンリスト
baudrate_var = ctk.StringVar()
baudrates = ["9600", "19200", "38400", "57600", "115200"]
baudrate_dropdown = ctk.CTkOptionMenu(app, variable=baudrate_var, values=baudrates)
baudrate_dropdown.grid(row=0, column=1,padx=0, pady=0)

# COMポートオープン
com_port_button = ctk.CTkButton(app, text="COM Port Open", command=open_serial_port)
com_port_button.grid(row=0,column=2, padx=0, pady=0)


# 送信データ入力
send_data_entry = ctk.CTkEntry(app, textvariable=send_data_var, width=200)
send_data_entry.grid(row=2, column=0, pady=10, padx=10)

# 送信ボタン
send_data_button = ctk.CTkButton(app, text="Send", command=send_serial_data)
send_data_button.grid(row=2, column=1, pady=10, padx=10)

close_port_button = ctk.CTkButton(app, text="COM Port Close", command=close_serial_port)
close_port_button.grid(row=2, column=2, pady=10, padx=10)

# 受信データ表示
received_data_label = ctk.CTkLabel(app, text="Received Data")
received_data_label.grid(row=3, column=0, pady=10, padx=10, sticky="w")
received_data_display = ctk.CTkTextbox(app, width=600, height=300)
received_data_display.grid(row=4, column=0, columnspan=2, pady=0, padx=0, sticky="nsew")

# デバッグ用printfエリア
printf_label = ctk.CTkLabel(app, text="Debug message")
printf_label.grid(row=3, column=2, padx=10, pady=10, sticky="w")
printf = ctk.CTkTextbox(app, width=300, height=300)
printf.grid(row=4, column=2, padx=2,pady=0, sticky="nsew")


# Enterキーが押されたときにsend_serial_data関数を呼び出すイベントバインディング
app.bind("<Return>", send_serial_data)

# アプリケーション終了時にシリアルポートを閉じる
app.protocol("WM_DELETE_WINDOW", destroy_application)

app.mainloop()