import os
import pickle
import face_recognition

def train_faces():
    os.makedirs("encodings", exist_ok=True)

    known_encodings = []
    known_names = []
    known_ids = []

    dataset_dir = "dataset"
    if not os.path.exists(dataset_dir):
        print(" No dataset folder found.")
        return False

    for person_folder in os.listdir(dataset_dir):
        person_path = os.path.join(dataset_dir, person_folder)
        if not os.path.isdir(person_path):
            continue

        try:
            person_id, person_name = person_folder.split("_", 1)
        except:
            continue

        for img_name in os.listdir(person_path):
            img_path = os.path.join(person_path, img_name)
            image = face_recognition.load_image_file(img_path)
            enc = face_recognition.face_encodings(image)

            if len(enc) > 0:
                known_encodings.append(enc[0])
                known_names.append(person_name)
                known_ids.append(person_id)

    data = {"encodings": known_encodings, "names": known_names, "ids": known_ids}

    with open("encodings/encodings.pkl", "wb") as f:
        pickle.dump(data, f)

    print(" Training complete. Encodings saved!")
    return True
