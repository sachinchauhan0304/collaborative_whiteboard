# app.py - Fixed Drawing App
import streamlit as st
from PIL import Image, ImageDraw
import numpy as np

# Initialize session state
if 'canvas' not in st.session_state:
    st.session_state.canvas = np.zeros((600, 800, 3), dtype=np.uint8) + 255  # White canvas
if 'drawing' not in st.session_state:
    st.session_state.drawing = False
if 'last_point' not in st.session_state:
    st.session_state.last_point = None
if 'tool' not in st.session_state:
    st.session_state.tool = "pen"
if 'color' not in st.session_state:
    st.session_state.color = "#000000"
if 'size' not in st.session_state:
    st.session_state.size = 5

# Tools panel
with st.sidebar:
    st.title("Drawing Tools")
    st.session_state.tool = st.radio(
        "Tool",
        ["pen", "rectangle", "circle", "line", "eraser"],
        horizontal=True
    )
    st.session_state.color = st.color_picker("Color", "#000000")
    st.session_state.size = st.slider("Size", 1, 20, 5)
    
    if st.button("Clear Canvas"):
        st.session_state.canvas = np.zeros((600, 800, 3), dtype=np.uint8) + 255
        st.session_state.drawing = False
        st.session_state.last_point = None
    
    if st.button("Save Canvas"):
        im = Image.fromarray(st.session_state.canvas)
        buf = io.BytesIO()
        im.save(buf, format="PNG")
        st.download_button(
            label="Download Drawing",
            data=buf.getvalue(),
            file_name="drawing.png",
            mime="image/png"
        )

# Drawing canvas using st.canvas
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color
    stroke_width=st.session_state.size,
    stroke_color=st.session_state.color,
    background_color="#ffffff",
    background_image=Image.fromarray(st.session_state.canvas) if st.session_state.canvas is not None else None,
    update_streamlit=True,
    height=600,
    width=800,
    drawing_mode="freedraw" if st.session_state.tool == "pen" else "transform",
    key="canvas",
)

# Handle drawing tools
if canvas_result.image_data is not None:
    if st.session_state.tool == "pen":
        st.session_state.canvas = canvas_result.image_data
    elif st.session_state.tool == "eraser":
        # Convert the drawing to white (eraser)
        white_drawing = np.where(canvas_result.image_data != np.array([255, 255, 255, 255]), 
                               np.array([255, 255, 255, 255], dtype=np.uint8),
                               st.session_state.canvas)
        st.session_state.canvas = white_drawing
    elif st.session_state.tool in ["rectangle", "circle", "line"]:
        # For shapes, we'll need to implement custom drawing
        pass

# Note: For full shape support, we would need additional code
# but this gives you working pen and eraser tools

# Add this at the top of your file:
from streamlit_drawable_canvas import st_canvas
