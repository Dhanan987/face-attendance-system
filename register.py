import cv2
import os
import time
from database import id_exists_in_dataset


def register_face(person_id, name, num_images=25):
    # 1) Check duplicate ID
    if id_exists_in_dataset(person_id):
        print(f"❌ This ID {person_id} already exists! Please use a new ID.")
        return

    folder_name = f"{person_id}_{name}".replace(" ", "_")
    save_dir = os.path.join("dataset", folder_name)
    os.makedirs(save_dir, exist_ok=True)

    # 3) Load face detector
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    # 4) Open camera
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print(" Camera not opening")
        return

    count = 0
    last_save_time = 0
    min_interval = 0.6  # seconds between saves

    print(f" Automatic capture started for: {person_id} {name}")
    print("➡ Sit in front of camera")
    print("➡ Move face slowly: center, left, right, up, down")
    print("➡ Press Q to stop early")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Camera frame not coming")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(120, 120)
        )

        status_text = "No face detected"

        
        if len(faces) > 0:
            # choose largest face
            x, y, w, h = max(faces, key=lambda box: box[2] * box[3])

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            face_img = frame[y:y + h, x:x + w]
            gray_face = gray[y:y + h, x:x + w]

           
            blur_score = cv2.Laplacian(gray_face, cv2.CV_64F).var()
            face_area = w * h

            good_size = face_area > 20000
            good_blur = blur_score > 80

            if good_size and good_blur:
                now = time.time()
                if now - last_save_time >= min_interval and count < num_images:
                    # resize saved image for consistency
                    face_img = cv2.resize(face_img, (224, 224))
                    img_path = os.path.join(save_dir, f"{count + 1}.jpg")
                    cv2.imwrite(img_path, face_img)
                    count += 1
                    last_save_time = now
                    status_text = f"Saved {count}/{num_images}"
                else:
                    status_text = f"Good face detected | Captured {count}/{num_images}"
            else:
                if not good_size:
                    status_text = "Come closer to camera"
                elif not good_blur:
                    status_text = "Hold still - image blurry"

        # text on screen
        cv2.putText(frame, f"ID: {person_id}  Name: {name}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.putText(frame, f"Captured: {count}/{num_images}", (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.putText(frame, status_text, (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        cv2.imshow("Automatic Face Registration", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            print("⚠ Registration stopped by user")
            break

        if count >= num_images:
            print(" Capture complete!")
            break

    cap.release()
    cv2.destroyAllWindows()

    if count > 0:
        print(f" Images saved in: {save_dir}")
    else:
        print(" No images captured")
