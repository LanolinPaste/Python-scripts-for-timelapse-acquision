These scripts are made to develop the timelapse acuqision platform using a camera and a shutter controller from different manufacturers and third-party libraries.
The platform assumes that the camera can be handled by OpenCV, and the shutter controller can receive either RS232C serial communication or TTL.

Procedures in brief:
1. Connect the camera with PC, install an OpenCV driver for the camera.
2. Install Python, cv2, and pyserial.
3. Try image acquisition with the Dshow.py script. Decide the best exposure and brightness for the sample you observe.
4. Connect the shutter controller with PC. When an RS232C connecter is available, use a USB-RS232C adaptor and a RS232C cable. When only a TTL connector is available, go to step 7.
5. Try shutter control with the Test_shutter_RS232C.py script. Commands for opening and closing the shutter depend on the controller.
6. Perform timelapse acquisition with the Timelapse_RS232C.py script.
7. To connect the PC to a TTL connector, prepare an Arduino UNO R3 or a similar third-party board, and a cable(s) which can connect the dupont connector to the TTL connector of the controller.
8. Install Arduino IDE and connect the Arduino. Compile the Shutter_arduino.ino sketch.
9. Connect Arduino to the shutter controller. Try shutter control with the Test_shutter_arduino.py script.
10. Perform timelapse acquisition with the Timelapse_arduino.py script.

Full procedures are documented below (Japanese only).
https://note.com/lively_auklet75/n/n0788743a78e9
