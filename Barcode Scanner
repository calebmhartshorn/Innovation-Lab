import cv2
from pyzbar.pyzbar import decode
import time
import json

# Load items from a file called items.txt
with open('items.txt', 'r') as f:
    items = {item['barcode']: item for item in json.load(f)}

scanned_barcodes = {}

def add_quantity(barcode):
    if barcode in items:
        item = items[barcode]
        print(f"Barcode: {barcode}")
        print(f"Name: {item['name']}")
        item['quantity_amount'] += 1
        print(f"New Quantity: {item['quantity_amount']} {item['quantity_unit']}")
    else:
        print(f"Barcode: {barcode}")
        print("This item is not in the database.")

def decode_barcode_from_webcam():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to capture image")
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        decoded_objects = decode(gray_frame)

        for obj in decoded_objects:
            barcode = obj.data.decode('utf-8')

            # 15 times seems good for how quick it scans
            if barcode in scanned_barcodes:
                scanned_barcodes[barcode] += 1
            else:
                scanned_barcodes[barcode] = 1

            if scanned_barcodes[barcode] == 15:
                time.sleep(1)  # Wait for 1 second
                scanned_barcodes[barcode] = 1

                cv2.rectangle(frame, (obj.rect.left, obj.rect.top),
                          (obj.rect.left + obj.rect.width, obj.rect.top + obj.rect.height),
                          (0, 255, 0), 2)
                cv2.putText(frame, barcode, (obj.rect.left, obj.rect.top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                add_quantity(barcode)

        cv2.imshow('Barcode Scanner', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

decode_barcode_from_webcam()
