import cv2
import numpy as np
import streamlit as st
from tensorflow.keras.applications.mobilenet_v2 import (
    MobileNetV2,
    preprocess_input,
    decode_predictions,
)
from PIL import Image


def load_model():
    return MobileNetV2(weights="imagenet")


def preprocess_image(image):
    img = np.array(image.convert("RGB"))
    img = cv2.resize(img, (224, 224))
    img = preprocess_input(img)
    img = np.expand_dims(img, axis=0)
    return img


def classify_image(model, image):
    try:
        processed = preprocess_image(image)
        predictions = model.predict(processed)
        return decode_predictions(predictions, top=3)[0]
    except Exception as e:
        st.error(f"Error classifying image: {str(e)}")
        return None


@st.cache_resource
def load_cached_model():
    return load_model()


def main():
    st.set_page_config(page_title="AI Image Classifier", layout="centered")

    st.title("AI Image Classifier")
    st.write("Upload an image and let AI tell you what is in it!")

    model = load_cached_model()

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)

        if st.button("Classify Image"):
            with st.spinner("Analyzing Image..."):
                predictions = classify_image(model, image)

            if predictions:
                st.subheader("Predictions")
                for _, label, score in predictions:
                    st.write(f"**{label}**: {score:.2%}")


if __name__ == "__main__":
    main()