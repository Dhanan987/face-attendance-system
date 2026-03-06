import cv2
import pickle
import numpy as np
import face_recognition
from datetime import datetime
import pandas as pd
import os

from database import init_db, insert_attendance, already_marked


def start_attendance(tolerance=0.50):
    init_db()
    os.makedirs("attendance_reports", exist_ok=True)

    enc_path = os.path.join("encodings", "encodings.pkl")
    if not os.path.exists(enc_path):
        print("❌ encodings/encodings.pkl not found. First run Train (Option 2).")
        return

    with open(enc_path, "rb") as f:
        data = pickle.load(f)

    known_encodings = data.get("encodings", [])
    known_names = data.get("names", [])
    known_ids = data.get("ids", [])

    if len(known_encodings) == 0:
        print("❌ No encodings found. Train again after capturing images.")
        return

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("❌ Camera not opening")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    excel_file = os.path.join("attendance_reports", f"attendance_{today}.xlsx")

    # ✅ this set remembers who already printed message in this run
    shown_today = set()

    print("✅ Attendance started (Press Q to quit)")

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("❌ Camera frame not coming")
            break

        small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb)
        face_encodings = face_recognition.face_encodings(rgb, face_locations)

        for (top, right, bottom, left), face_enc in zip(face_locations, face_encodings):
            name = "Unknown"
            pid = "Unknown"

            distances = face_recognition.face_distance(known_encodings, face_enc)
            if len(distances) > 0:
                best = int(np.argmin(distances))
                best_dist = float(distances[best])

                if best_dist < tolerance:
                    name = str(known_names[best])
                    pid = str(known_ids[best])

                    key = (pid, today)  # unique for that day

                    now = datetime.now()
                    time_str = now.strftime("%H:%M:%S")

                    if not already_marked(pid, today):
                        insert_attendance(pid, name, today, time_str)

                        row = {"ID": pid, "Name": name, "Date": today, "Time": time_str}
                        if not os.path.exists(excel_file):
                            pd.DataFrame([row]).to_excel(excel_file, index=False)
                        else:
                            df_existing = pd.read_excel(excel_file)
                            df_new = pd.concat([df_existing, pd.DataFrame([row])], ignore_index=True)
                            df_new.to_excel(excel_file, index=False)

                        # ✅ print only once
                        if key not in shown_today:
                            print(f"✅ Marked: {pid} {name}")
                            shown_today.add(key)

                    else:
                        # ✅ print only once
                        if key not in shown_today:
                            print(f"⚠ Already marked today: {pid} {name}")
                            shown_today.add(key)

            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, f"{pid} {name}", (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("Face Attendance System", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("✅ Attendance stopped.")
