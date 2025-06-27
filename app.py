# app.py - CollabDraw Streamlit Version
import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
import io
import base64

# Initialize session state
if 'canvas' not in st.session_state:
    st.session_state.canvas = Image.new("RGB", (800, 600), "white")
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
        st.session_state.canvas = Image.new("RGB", (800, 600), "white")
    
    if st.button("Save Canvas"):
        buf = io.BytesIO()
        st.session_state.canvas.save(buf, format="PNG")
        st.download_button(
            label="Download Drawing",
            data=buf.getvalue(),
            file_name="collabdraw.png",
            mime="image/png"
        )

# Drawing canvas
canvas = st.session_state.canvas.copy()
draw = ImageDraw.Draw(canvas)

# Convert to bytes for display
img_bytes = io.BytesIO()
canvas.save(img_bytes, format='PNG')
img_data = img_bytes.getvalue()

# Create clickable image
clicked = st.image(img_data, use_column_width=True, caption="Draw on the canvas")

# Mouse event handling
if clicked:
    mouse_coords = st.session_state.get("mouse_coords", None)
    
    if mouse_coords:
        x, y = mouse_coords["x"], mouse_coords["y"]
        
        if st.session_state.drawing:
            if st.session_state.last_point:
                # Draw based on tool
                if st.session_state.tool == "pen":
                    draw.line(
                        [st.session_state.last_point, (x, y)],
                        fill=st.session_state.color,
                        width=st.session_state.size
                    )
                elif st.session_state.tool == "eraser":
                    draw.line(
                        [st.session_state.last_point, (x, y)],
                        fill="white",
                        width=st.session_state.size
                    )
                elif st.session_state.tool == "line":
                    # For line, we'll draw on mouse up
                    pass
                    
            st.session_state.last_point = (x, y)
        else:
            st.session_state.drawing = True
            st.session_state.last_point = (x, y)
    else:
        st.session_state.drawing = False
        if st.session_state.tool == "line" and st.session_state.last_point:
            draw.line(
                [st.session_state.last_point, (x, y)],
                fill=st.session_state.color,
                width=st.session_state.size
            )

# Save the modified canvas
st.session_state.canvas = canvas

# JavaScript for mouse coordinates
st.components.v1.html(f"""
<script>
const img = document.querySelector('.stImage img');
if (img) {{
    img.onclick = (e) => {{
        const rect = e.target.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        Streamlit.setComponentValue({{x: x, y: y}});
    }}
}}
</script>
""", height=0)

# Run with: streamlit run app.py
