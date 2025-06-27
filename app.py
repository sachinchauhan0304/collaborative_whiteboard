# app.py
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import io

st.set_page_config(layout="wide")

# Sidebar tools
st.sidebar.title("Drawing Tools")
tool = st.sidebar.radio("Tool", ["freedraw", "line", "rect", "circle", "transform"])
stroke_width = st.sidebar.slider("Stroke width: ", 1, 20, 5)
stroke_color = st.sidebar.color_picker("Stroke color", "#FF0000")
bg_color = st.sidebar.color_picker("Background color", "#FFFFFF")
bg_image = None
realtime_update = st.sidebar.checkbox("Update in realtime", True)

# Canvas component
canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 0.0)",  # Transparent fill
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    background_image=bg_image,
    update_streamlit=realtime_update,
    height=500,
    width=800,
    drawing_mode=tool,
    key="canvas",
)

# Save canvas button
if st.sidebar.button("Save Canvas"):
    if canvas_result.image_data is not None:
        img = Image.fromarray(canvas_result.image_data.astype("uint8"))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.download_button(
            label="Download Drawing",
            data=buf.getvalue(),
            file_name="drawing.png",
            mime="image/png"
        )
