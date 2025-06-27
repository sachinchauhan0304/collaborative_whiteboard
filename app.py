# app.py - FULL WORKING VERSION
import streamlit as st
from streamlit_drawable_canvas import st_canvas  # <-- MAKE SURE THIS PACKAGE IS INSTALLED
import numpy as np
from PIL import Image
import io

# 1. FIRST INSTALL REQUIRED PACKAGE (run this in terminal):
# pip install streamlit-drawable-canvas numpy pillow

# 2. SET PAGE CONFIG (you can customize this)
st.set_page_config(
    page_title="CollabDraw Whiteboard",
    page_icon=":pencil2:",
    layout="wide"
)

# 3. INITIALIZE SESSION STATE (no changes needed here)
if 'tool' not in st.session_state:
    st.session_state.tool = "freedraw"
if 'color' not in st.session_state:
    st.session_state.color = "#000000"
if 'size' not in st.session_state:
    st.session_state.size = 5
if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#FFFFFF"
if 'canvas_key' not in st.session_state:
    st.session_state.canvas_key = "default"

# 4. SIDEBAR CONTROLS (customize tools/colors if needed)
with st.sidebar:
    st.title("🛠️ Tools")
    
    # Tool selection - change emoji/icons if desired
    st.session_state.tool = st.radio(
        "Drawing Tool:",
        ["freedraw", "line", "rect", "circle", "transform"],
        format_func=lambda x: {
            "freedraw": "✏️ Pen",
            "line": "📏 Line", 
            "rect": "🟦 Rectangle",
            "circle": "⭕ Circle",
            "transform": "✋ Select"
        }[x]
    )
    
    # Color pickers - change default colors if needed
    st.session_state.color = st.color_picker("Line Color", st.session_state.color)
    st.session_state.size = st.slider("Brush Size", 1, 30, st.session_state.size)
    st.session_state.bg_color = st.color_picker("Background", st.session_state.bg_color)
    
    # Action buttons
    if st.button("🧹 Clear Canvas"):
        st.session_state.canvas_key = str(hash("new_canvas"))  # Reset canvas
    if st.button("💾 Save Drawing"):
        pass  # Handled below

# 5. MAIN CANVAS AREA (change width/height if needed)
st.title("🎨 Collaborative Whiteboard")
canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 0.3)",
    stroke_width=st.session_state.size,
    stroke_color=st.session_state.color,
    background_color=st.session_state.bg_color,
    height=600,
    width=800,
    drawing_mode=st.session_state.tool,
    key=f"canvas_{st.session_state.canvas_key}",
    update_streamlit=True
)

# 6. SAVE FUNCTIONALITY (no changes needed)
if canvas_result.image_data is not None:
    img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.download_button(
        "⬇️ Download Drawing",
        buf.getvalue(),
        "whiteboard.png",
        "image/png"
    )

# 7. INSTRUCTIONS (customize if needed)
with st.expander("ℹ️ Instructions"):
    st.write("""
    - Draw with mouse/touchpad
    - Change tools from sidebar
    - Adjust colors and brush size
    - Save or clear when done
    """)
