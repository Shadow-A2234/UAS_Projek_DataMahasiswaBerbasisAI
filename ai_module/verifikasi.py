import cv2
import mediapipe as mp
import time
import os
import webbrowser
from tkinter import Tk, Label
from PIL import Image, ImageTk

# Konfigurasi file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_FILE = os.path.join(BASE_DIR, "opening.mp4")
OUTLINE_FILE = os.path.join(BASE_DIR, "hand_outline.png")
ACTIVATION_DURATION = 0.5  # detik

# Fungsi overlay tangan
def overlay_transparent(background, overlay, x, y, alpha_factor=0.6):
    if overlay.shape[2] < 4:
        return background

    bh, bw = background.shape[:2]
    h, w = overlay.shape[:2]

    if x + w > bw or y + h > bh or x < 0 or y < 0:
        return background

    overlay_resized = overlay[:, :, :3]
    alpha_overlay = overlay[:, :, 3] / 255.0 * alpha_factor
    alpha_bg = 1.0 - alpha_overlay

    for c in range(3):
        background[y:y+h, x:x+w, c] = (
            alpha_overlay * overlay_resized[:, :, c] +
            alpha_bg * background[y:y+h, x:x+w, c]
        )
    return background

# Cek apakah tangan di tengah
def is_hand_in_center(landmarks, width, height):
    x = landmarks.landmark[0].x * width
    y = landmarks.landmark[0].y * height
    return width * 0.35 < x < width * 0.65 and height * 0.35 < y < height * 0.65

# Fungsi putar video fullscreen dengan GUI
def play_video_gui(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("❌ Gagal membuka video.")
        return

    root = Tk()
    root.title("Opening Video")
    root.attributes("-fullscreen", True)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    label = Label(root)
    label.pack()

    def update_frame():
        ret, frame = cap.read()
        if not ret:
            root.destroy()
            return

        frame = cv2.resize(frame, (screen_width, screen_height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(image=Image.fromarray(frame))
        label.config(image=img)
        label.image = img
        root.after(30, update_frame)

    def exit_on_esc(event):
        root.destroy()

    root.bind("<Escape>", exit_on_esc)
    update_frame()
    root.mainloop()
    cap.release()

# Main program verifikasi
def main():
    if not os.path.exists(OUTLINE_FILE) or not os.path.exists(VIDEO_FILE):
        print("❌ File outline atau video tidak ditemukan.")
        return

    cap = cv2.VideoCapture(0)
    time.sleep(1.5)

    if not cap.isOpened():
        print("❌ Tidak dapat membuka kamera.")
        return

    hand_overlay = cv2.imread(OUTLINE_FILE, cv2.IMREAD_UNCHANGED)
    hand_overlay = cv2.resize(hand_overlay, (200, 200))

    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

    with mp_hands.Hands(max_num_hands=1,
                        min_detection_confidence=0.75,
                        min_tracking_confidence=0.75) as hands:

        start_time = None
        video_played = False

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            ox, oy = w // 2 - 100, h // 2 - 100
            frame = overlay_transparent(frame, hand_overlay, ox, oy, 0.5)

            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(image_rgb)

            if results.multi_hand_landmarks:
                landmarks = results.multi_hand_landmarks[0]
                mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

                if is_hand_in_center(landmarks, w, h):
                    cv2.putText(frame, "SIAP!", (w // 2 - 60, h // 2 - 160),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 255, 0), 4)

                    if start_time is None:
                        start_time = time.time()
                    elif time.time() - start_time >= ACTIVATION_DURATION and not video_played:
                        print("✅ Tangan terdeteksi di tengah — Putar video.")
                        play_video_gui(VIDEO_FILE)
                        video_played = True

                        # ✅ Buka halaman chat_page otomatis
                        webbrowser.open("http://localhost:5000/chat_page")
                        break
                else:
                    start_time = None
            else:
                start_time = None

            cv2.putText(frame, "Letakkan tangan di outline", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.imshow("Sensor Tangan", frame)
            if cv2.waitKey(1) & 0xFF in [27, ord('q')]:
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
