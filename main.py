from cryptography.fernet import Fernet
import face_recognition
import cv2
import pickle
import os
import numpy as np
import tkinter as tk
from tkinter import messagebox

# Generate a key for encryption/decryption
# Store this key securely; only the system should have access to it
key = Fernet.generate_key()
cipher_suite = Fernet(key)

class Dlib_Face_Unlock:
    def __init__(self):
        try:
            with open(r'C:\Users\krish\Downloads\Face-Recognition-Login-main\labels.pickle', 'rb') as self.f:
                self.og_labels = pickle.load(self.f)
            print(self.og_labels)
        except FileNotFoundError:
            print("No label.pickle file detected, will create required pickle files")

        self.current_id = 0
        self.labels_ids = {}
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.image_dir = os.path.join(self.BASE_DIR, 'images')
        for self.root, self.dirs, self.files in os.walk(self.image_dir):
            for self.file in self.files:
                if self.file.endswith('.enc'):  # Encrypted image files
                    self.path = os.path.join(self.root, self.file)
                    self.label = os.path.basename(os.path.dirname(self.path)).replace(' ', '-').lower()
                    if not self.label in self.labels_ids:
                        self.labels_ids[self.label] = self.current_id
                        self.current_id += 1
                        self.id = self.labels_ids[self.label]

        print(self.labels_ids)
        self.og_labels = 0
        if self.labels_ids != self.og_labels:
            with open('labels.pickle', 'wb') as self.file:
                pickle.dump(self.labels_ids, self.file)

            self.known_faces = []
            for self.i in self.labels_ids:
                noOfImgs = len([filename for filename in os.listdir('images/' + self.i)
                                if os.path.isfile(os.path.join('images/' + self.i, filename))])
                print(noOfImgs)
                for imgNo in range(1, (noOfImgs + 1)):
                    self.directory = os.path.join(self.image_dir, self.i, str(imgNo) + '.enc')
                    # Decrypt image before loading it for face recognition
                    decrypted_image = decrypt_image(self.directory)
                    self.img = face_recognition.load_image_file(decrypted_image)
                    self.img_encoding = face_recognition.face_encodings(self.img)[0]
                    self.known_faces.append([self.i, self.img_encoding])
            print(self.known_faces)
            print("No Of Imgs" + str(len(self.known_faces)))
            with open('KnownFace.pickle', 'wb') as self.known_faces_file:
                pickle.dump(self.known_faces, self.known_faces_file)
        else:
            with open(r'C:\Users\krish\Downloads\Face-Recognition-Login-main\KnownFace.pickle', 'rb') as self.faces_file:
                self.known_faces = pickle.load(self.faces_file)
            print(self.known_faces)

    def ID(self):
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.face_names = []
        while self.running == True:
            self.ret, self.frame = self.cap.read()
            self.small_frame = cv2.resize(self.frame, (0, 0), fx=0.5, fy=0.5)
            self.rgb_small_frame = self.small_frame[:, :, ::-1]
            if self.running:
                self.face_locations = face_recognition.face_locations(self.frame)
                self.face_encodings = face_recognition.face_encodings(self.frame, self.face_locations)
                self.face_names = []
                for self.face_encoding in self.face_encodings:
                    for self.face in self.known_faces:
                        self.matches = face_recognition.compare_faces([self.face[1]], self.face_encoding)
                        self.name = 'Unknown'
                        self.face_distances = face_recognition.face_distance([self.face[1]], self.face_encoding)
                        self.best_match = np.argmin(self.face_distances)
                        if self.matches[self.best_match] == True:
                            self.running = False
                            self.face_names.append(self.face[0])
                            break
            self.cap.release()
            cv2.destroyAllWindows()
            break
        return self.face_names

# Encryption and Decryption Functions
def encrypt_image(image_path):
    with open(image_path, 'rb') as file:
        image_data = file.read()
    encrypted_data = cipher_suite.encrypt(image_data)
    encrypted_path = image_path.replace(".png", ".enc")
    with open(encrypted_path, 'wb') as file:
        file.write(encrypted_data)
    os.remove(image_path)  # Remove the unencrypted file
    return encrypted_path

def decrypt_image(encrypted_path):
    with open(encrypted_path, 'rb') as file:
        encrypted_data = file.read()
    decrypted_data = cipher_suite.decrypt(encrypted_data)
    decrypted_path = encrypted_path.replace(".enc", "_temp.png")
    with open(decrypted_path, 'wb') as file:
        file.write(decrypted_data)
    return decrypted_path

def register():
    if not os.path.exists("images"):
        os.makedirs("images")
    name_folder = name.get().lower()
    os.makedirs(os.path.join("images", name_folder), exist_ok=True)  # Create user folder

    numberOfFile = len([filename for filename in os.listdir(os.path.join('images', name_folder))
                        if os.path.isfile(os.path.join('images', name_folder, filename))])
    numberOfFile += 1  # Increment file number for the new image
    cam = cv2.VideoCapture(0)

    cv2.namedWindow("test")
    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame")
            break
        cv2.imshow("test", frame)
        k = cv2.waitKey(1)
        if k % 256 == 27:
            print("Escape hit, closing...")
            break
        elif k % 256 == 32:
            img_name = os.path.join("images", name_folder, str(numberOfFile) + ".png")
            cv2.imwrite(img_name, frame)
            encrypt_image(img_name)  # Encrypt the image
            print(f"{img_name} written and encrypted!")
            break

    cam.release()
    cv2.destroyAllWindows()
    raiseFrame(loginFrame)  # Raise the login frame after registration


def login():
    dfu = Dlib_Face_Unlock()
    user = dfu.ID()
    if user == []:
        messagebox.showerror("Alert", "Sorry, Your face is not Recognised")
        return
    loggedInUser.set(user[0])
    raiseFrame(userMenuFrame)


root = tk.Tk()
root.title("Menu")
root.geometry("800x600")
root.config(bg="#1976D2")  # Set the background color to blue

loginFrame = tk.Frame(root, bg="#BBDEFB")  # Set the background color to a lighter shade of blue
regFrame = tk.Frame(root, bg="#BBDEFB")  # Set the background color to a lighter shade of blue
userMenuFrame = tk.Frame(root, bg="#BBDEFB")  # Set the background color to a lighter shade of blue

# Define Frame List
frameList = [loginFrame, regFrame, userMenuFrame]
# Configure all Frames
for frame in frameList:
    frame.grid(row=0, column=0, sticky='news')


def raiseFrame(frame):
    frame.tkraise()


def regFrameRaiseFrame():
    raiseFrame(regFrame)


def logFrameRaiseFrame():
    raiseFrame(loginFrame)


name = tk.StringVar()
loggedInUser = tk.StringVar()

tk.Label(loginFrame, text="Face Recognition Model", font=("Courier", 30), bg="#BBDEFB").pack(pady=20)
loginButton = tk.Button(loginFrame, text="Login", bg="#1976D2", fg="white", font=("Arial", 20), command=login)
loginButton.pack(pady=10)
regButton = tk.Button(loginFrame, text="Register", command=regFrameRaiseFrame, bg="#1976D2", fg="white",
                      font=("Arial", 20))
regButton.pack(pady=10)

tk.Label(regFrame, text="Register", font=("Courier", 30), bg="#BBDEFB").pack(pady=20)
tk.Label(regFrame, text="Name: ", font=("Arial", 20), bg="#BBDEFB").pack(pady=10)
nameEntry = tk.Entry(regFrame, textvariable=name, font=("Arial", 20))
nameEntry.pack(pady=10)

registerButton = tk.Button(regFrame, text="Registration", command=register, bg="#1976D2", fg="white",
                           font=("Arial", 20))
registerButton.pack(pady=10)

tk.Label(userMenuFrame, text="Welcome, ", font=("Courier", 30), bg="#BBDEFB").pack(pady=20)
tk.Label(userMenuFrame, textvariable=loggedInUser, font=("Courier", 30), bg="#BBDEFB", fg="red").pack(pady=10)
tk.Button(userMenuFrame, text="Back", font=("Arial", 20), command=logFrameRaiseFrame, bg="#1976D2", fg="white").pack(
    pady=10)

dfu = Dlib_Face_Unlock()
raiseFrame(loginFrame)
root.mainloop()
