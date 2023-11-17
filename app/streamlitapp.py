# Import all of the dependencies
import streamlit as st
import os
import imageio
import numpy as np
from PIL import Image
import tensorflow as tf
from utils import load_data, num_to_char
from modelutil import load_model
import zipfile

# Set the layout to the streamlit app as wide
st.set_page_config(layout="wide")

# Setup the sidebar
with st.sidebar:
    st.image("https://www.onepointltd.com/wp-content/uploads/2020/03/inno2.png")
    st.title("LipNet")
    st.info(
        "This application is originally developed from the LipNet deep learning model."
    )

st.title("Lip Neural Network Architecture")
# Generating a list of options or videos
options = os.listdir(os.path.join("..", "data", "s1"))
selected_video = st.selectbox("Choose video", options)

# Generate two columns
col1, col2 = st.columns(2)

if options:
    # Rendering the video
    with col1:
        st.info("The video below displays the converted video in mp4 format")
        file_path = os.path.join("..", "data", "s1", selected_video)
        os.system(f"ffmpeg -i {file_path} -vcodec libx264 test_video.mp4 -y")

        # Rendering inside the app
        video = open("test_video.mp4", "rb")
        video_bytes = video.read()
        st.video(video_bytes)

    with col2:
        st.info("This is all the machine learning model sees when making a prediction")
        video, annotations = load_data(tf.convert_to_tensor(file_path))
        frames = [
            Image.fromarray((np.squeeze(frame.numpy()) * 255).astype(np.uint8))
            for frame in video
        ]
        imageio.mimsave("animation.gif", frames, duration=0.1)
        st.image("animation.gif", width=400)

        st.info("This is the output of the machine learning model as tokens")

        # Extract weights from zip file
        # zip_file_path = "..\\models\\models - checkpoint 50.zip"
        # extracted_folder_path = "..\\models\\extracted_checkpoints"
        # with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        #    zip_ref.extractall(extracted_folder_path)

        model = load_model()
        yhat = model.predict(tf.expand_dims(video, axis=0))
        decoder = tf.keras.backend.ctc_decode(yhat, [75], greedy=True)[0][0].numpy()
        st.text(decoder)

        # Convert prediction to text
        st.info("Decode the raw tokens into words")
        converted_prediction = (
            tf.strings.reduce_join(num_to_char(decoder)).numpy().decode("utf-8")
        )
        st.text(converted_prediction)
