import cv2
import pandas as pd
import numpy as np
from ultralytics import YOLO
from tracker import *
import cvzone

from db.db_counter import get_connection, start_run, log_crossing, finish_run

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
VIDEO_PATH = PROJECT_ROOT / "data" / "videos" / "vidp.mp4"

model = YOLO('yolov8s.pt')


def RGB(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        point = [x, y]
        print(point)


cv2.namedWindow('RGB')
cv2.setMouseCallback('RGB', RGB)
cap = cv2.VideoCapture(str(VIDEO_PATH))
if not cap.isOpened():
    raise RuntimeError(f"Cannot open video: {VIDEO_PATH}")

output = cv2.VideoWriter('output_final.avi', cv2.VideoWriter_fourcc(*'MPEG'), 30, (1020, 500))

with open('coco.names', 'r') as file:
    class_list = file.read().split('\n')

# --- database setup ---
fps = cap.get(cv2.CAP_PROP_FPS) or 30
conn = get_connection()
run_id = start_run(conn, str(VIDEO_PATH))

count = 0
persondown = {}
tracker = Tracker()
counter1 = []   # people going DOWN

personup = {}
counter2 = []   # people going UP

cy1 = 194
cy2 = 220
offset = 6

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        count += 1
        if count % 3 != 0:
            continue

        frame = cv2.resize(frame, (1020, 500))

        results = model.predict(frame)

        a = results[0].boxes.data
        px = pd.DataFrame(a).astype("float")

        detections = []

        for index, row in px.iterrows():
            x1 = int(row[0])
            y1 = int(row[1])
            x2 = int(row[2])
            y2 = int(row[3])
            d = int(row[5])

            c = class_list[d]
            if 'person' in c:
                detections.append([x1, y1, x2, y2])

        bbox_id = tracker.update(detections)
        video_time = count / fps

        for bbox in bbox_id:
            x3, y3, x4, y4, id = bbox
            cx = int(x3 + x4) // 2
            cy = int(y3 + y4) // 2
            cv2.circle(frame, (cx, cy), 4, (255, 0, 255), -1)

            ## for down going
            if cy1 < (cy + offset) and cy1 > cy - offset:
                cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 0, 255), 2)
                cvzone.putTextRect(frame, f'{id}', (x3, y3), 1, 2)
                persondown[id] = (cx, cy)

            if id in persondown:
                if cy2 < (cy + offset) and cy2 > cy - offset:
                    cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 255), 2)
                    cvzone.putTextRect(frame, f'{id}', (x3, y3), 1, 2)
                    if counter1.count(id) == 0:
                        counter1.append(id)
                        log_crossing(conn, run_id, id, 'down', video_time)

            ## for up going
            if cy2 < (cy + offset) and cy2 > cy - offset:
                cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)
                cvzone.putTextRect(frame, f'{id}', (x3, y3), 1, 2)
                personup[id] = (cx, cy)

            if id in personup:
                if cy1 < (cy + offset) and cy1 > cy - offset:
                    cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 255), 2)
                    cvzone.putTextRect(frame, f'{id}', (x3, y3), 1, 2)
                    if counter2.count(id) == 0:
                        counter2.append(id)
                        log_crossing(conn, run_id, id, 'up', video_time)

        cv2.line(frame, (3, cy1), (1018, cy1), (0, 255, 0), 2)
        cv2.line(frame, (5, cy2), (1019, cy2), (0, 255, 255), 2)

        downcount = len(counter1)
        upcount = len(counter2)

        cvzone.putTextRect(frame, f'Down: {downcount}', (50, 60), 2, 2)
        cvzone.putTextRect(frame, f'Up: {upcount}', (50, 160), 2, 2)
        output.write(frame)
        cv2.imshow('RGB', frame)
        if cv2.waitKey(1) & 0xff == 27:
            break

finally:
    # always runs, even if the script crashes or you press ESC
    finish_run(conn, run_id, len(counter2), len(counter1))
    conn.close()
    cap.release()
    output.release()
    cv2.destroyAllWindows()
    print(f"Run {run_id} saved: Up={len(counter2)}, Down={len(counter1)}, "
          f"Total={len(counter2) - len(counter1)}")