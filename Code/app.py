import socket
import random
import json

def web_page(gpio_state):
    if led.value() == 1:
        gpio_state="ON"
    else:
        gpio_state="OFF"
    return json.dumps({'GPIO_State': gpio_state})

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024).decode()  # Decode bytes to string
    print('Content = %s' % request)
    led_on = request.find('/?led=on')
    led_off = request.find('/?led=off')
    if led_on != -1:
        print('LED ON')
        gpio_state = "ON"
    elif led_off != -1:
        print('LED OFF')
        gpio_state = "OFF"
    else:
        gpio_state = random.choice(["on", "off"])

    response = web_page(gpio_state)

    # Add CORS headers
    conn.send(b'HTTP/1.1 200 OK\n')
    conn.send(b'Content-Type: application/json\n')
    conn.send(b'Access-Control-Allow-Origin: *\n')  # Allow requests from any origin
    conn.send(b'Connection: close\n\n')
    conn.sendall(response.encode('utf-8'))
    conn.close()
