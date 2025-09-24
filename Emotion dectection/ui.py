import streamlit as st
import cv2
import numpy as np
from keras.models import load_model
from PIL import Image
import time

# Load the trained model
model = load_model('model_file_30epochs.h5')
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Emotion labels
labels_dict = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Neutral', 5: 'Sad', 6: 'Surprise'}

# Set page configuration
st.set_page_config(page_title="Emotion Detection System", page_icon="😊", layout="wide")

# Title and Sidebar Options
st.markdown("<h1 style='text-align: center;'>Emotion Detection System</h1>", unsafe_allow_html=True)
st.sidebar.title("🎛️ Options")
option = st.sidebar.radio("Choose Input Type", ("📸 Upload Image", "🎥 Use Webcam"))

def predict_emotion(img):
    """Detects faces and predicts emotions."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 3)

    if len(faces) == 0:
        return img, None  # No faces detected

    for (x, y, w, h) in faces:
        sub_face_img = gray[y:y+h, x:x+w]
        resized = cv2.resize(sub_face_img, (48, 48))
        normalized = resized / 255.0
        reshaped = np.reshape(normalized, (1, 48, 48, 1))
        
        result = model.predict(reshaped)
        label = np.argmax(result, axis=1)[0]
        
        # Draw face rectangle and emotion label
        cv2.rectangle(img, (x, y), (x + w, y + h), (50, 50, 255), 2)
        cv2.putText(img, labels_dict[label], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    return img, label

if option == "📸 Upload Image":
    st.subheader("📂 Upload an Image for Emotion Detection")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        image = np.array(image)

        # Convert image to BGR format (PIL loads in RGB, OpenCV uses BGR)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        with st.spinner("🔍 Analyzing image..."):
            time.sleep(2)  # Simulate loading
            result_img, detected_emotion = predict_emotion(image)

        if detected_emotion is not None:
            st.image(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB), caption=f"Detected Emotion: {labels_dict[detected_emotion]}", use_container_width=True)
        else:
            st.warning("⚠️ No face detected. Try another image.")

elif option == "🎥 Use Webcam":
    st.subheader("📹 Real-time Emotion Detection (Press 'Stop' to exit)")
    FRAME_WINDOW = st.image([])
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        result_img, detected_emotion = predict_emotion(frame)

        # Convert BGR to RGB for Streamlit display
        result_img = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)
        FRAME_WINDOW.image(result_img, use_container_width=True)

    cap.release()
    cv2.destroyAllWindows()
