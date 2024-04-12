from imagebind import data
import torch
from imagebind.models import imagebind_model
from imagebind.models.imagebind_model import ModalityType
import os

from PIL import Image
import streamlit as st
import tempfile

device = "cuda:0" if torch.cuda.is_available() else "cpu"

# Instantiate model
model = imagebind_model.imagebind_huge(pretrained=True)
model.eval()
model.to(device)

text_list = ["An Advertisement(branding, text, promotions, lifestyle depiction, contextual cues, and visual composition)","Not an Advertisement"]
image_paths = []

text = ['Advertisement Creative(Contains Text)', 'Not an Advertisement Creative(Contains No Text)', 'Simple Product Image and not an Advertisement)']



st.title("ImageBind")

# Upload image
uploaded_image = st.file_uploader("Choose an image...", type= ["png", "jpg", "jpeg"])


if uploaded_image is not None:
    temp_dir = tempfile.mkdtemp()
    path = os.path.join(temp_dir, uploaded_image.name)
    with open(path, "wb") as f:
        f.write(uploaded_image.getvalue())

    image_paths.append(path)
    image = Image.open(uploaded_image)
    st.image(image, caption="Uploaded Image.", use_column_width=True)


    inputs = {
        ModalityType.TEXT: data.load_and_transform_text(text_list, device),
        ModalityType.VISION: data.load_and_transform_vision_data(image_paths, device),
    }

    with torch.no_grad():
        embeddings = model(inputs)

    softmax_output = torch.softmax(embeddings[ModalityType.VISION] @ embeddings[ModalityType.TEXT].T, dim=-1)

    if softmax_output[0][0] > softmax_output[0][1]:
        st.write("Advertisement")
    else:
        st.write("Not an Advertisement")