import serial
import time

# 1. Set Arduino COM port and baudrate
arduino = serial.Serial('COM4', 9600)  # <<< Please check your Arduino COM port and baudrate
time.sleep(2)  # Wait for Arduino to reset
print("Arduino is ready! Please enter a command. Enter Q to exit the program.")

# 2. Repeatedly prompt user for input and send to Arduino
while True:
    command = input("Enter command (Q to quit): ").strip().upper()

    if command == 'Q':
        print("Exiting program")
        break

    # No longer limited to A~F, any input will be sent
    arduino.write(command.encode())
    print("Sent:", command)

    time.sleep(6)  # <<< You can adjust the wait time here
    while arduino.in_waiting > 0:
        response = arduino.readline().decode().strip()
        print("Arduino:", response)

# 3. Close the connection
arduino.close()
