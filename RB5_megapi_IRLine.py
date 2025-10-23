import serial
import time

def flush_serial_buffer(ser):
    print("Flushing serial buffer for startup junk...")
    time.sleep(0.5)
    while ser.in_waiting:
        flushed = ser.read(ser.in_waiting)
        print(f"Flushed bytes: {flushed}")

def read_analog_sensor(ser, port, timeout=2.0):
    print(f"\nRequesting sensor reading at A{port}")
    command = bytes([0xFF, 0x55, 0x04, 0x01, 0x01, 0x1F, port, 0x00])
    ser.reset_input_buffer()
    ser.write(command)
    print(f"Sent command: {[hex(b) for b in command]}")

    response = b''
    start_time = time.time()
    while True:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            response += data
            print(f"Read {len(data)} bytes: {data}")
            if b'\xFF\x55' in response:
                print("Detected packet header.")
                break
        if time.time() - start_time > timeout:
            print(f"Timeout waiting for sensor at A{port}. Last data: {response}")
            return None

    idx = response.find(b'\xFF\x55')
    payload = response[idx + 2:]
    print(f"Payload bytes: {list(payload)}")

    # Ignore first 3 bytes (index, datatype, marker), then read until CR/LF
    ascii_bytes = []
    for b in payload[3:]:
        if b in (13, 10):  # skip CR/LF
            continue
        ascii_bytes.append(b)

    try:
        string_val = bytes(ascii_bytes).decode('ascii')
        value = int(string_val)
    except Exception as e:
        print(f"Failed to decode ASCII: {e}")
        value = None

    print(f"Decoded sensor value at A{port}: {value}")
    return value

if __name__ == "__main__":
    serial_port = '/dev/ttyUSB0'  # Adjust if needed
    baud_rate = 115200

    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    time.sleep(1)  # Wait for serial port readiness
    
    flush_serial_buffer(ser)  # Clean startup garbage

    for analog_port in [6, 7, 8, 9, 10]:
        sensor_value = read_analog_sensor(ser, analog_port)
        print(f"Final sensor value at A{analog_port}: {sensor_value}")

    ser.close()
