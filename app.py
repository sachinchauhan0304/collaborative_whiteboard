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
if 'start_point' not in st.session_state:  # For shapes that need a start point
    st.session_state.start_point = None

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
        st.session_state.drawing = False
        st.session_state.last_point = None
        st.session_state.start_point = None
    
    if st.button("Save Canvas"):
        buf = io.BytesIO()
        st.session_state.canvas.save(buf, format="PNG")
        st.download_button(
            label="Download Drawing",
            data=buf.getvalue(),
            file_name="collabdraw.png",
            mime="image/png"
        )

# Create a placeholder for the canvas
canvas_placeholder = st.empty()

# Display the canvas
canvas = st.session_state.canvas.copy()
draw = ImageDraw.Draw(canvas)

# Convert to bytes for display
img_bytes = io.BytesIO()
canvas.save(img_bytes, format='PNG')
img_data = img_bytes.getvalue()

# Display the image in the placeholder
canvas_placeholder.image(img_data, use_container_width=True, caption="Draw on the canvas")

# Mouse event handling using streamlit's built-in click events
mouse_clicked = st.session_state.get("mouse_clicked", False)
mouse_x = st.session_state.get("mouse_x", 0)
mouse_y = st.session_state.get("mouse_y", 0)

# JavaScript for mouse coordinates
st.components.v1.html(f"""
<script>
const img = document.querySelector('.stImage img');
if (img) {{
    img.onmousedown = (e) => {{
        const rect = e.target.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        Streamlit.setComponentValue({{mouse_clicked: true, mouse_x: x, mouse_y: y}});
    }}
    
    img.onmousemove = (e) => {{
        if (e.buttons === 1) {{  // Only if left button is pressed
            const rect = e.target.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            Streamlit.setComponentValue({{mouse_clicked: true, mouse_x: x, mouse_y: y}});
        }}
    }}
    
    img.onmouseup = (e) => {{
        const rect = e.target.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        Streamlit.setComponentValue({{mouse_clicked: true, mouse_x: x, mouse_y: y, mouse_up: true}});
    }}
}}
</script>
""", height=0)

# Handle drawing based on mouse events
if mouse_clicked:
    if not st.session_state.drawing:
        # Start drawing
        st.session_state.drawing = True
        st.session_state.last_point = (mouse_x, mouse_y)
        st.session_state.start_point = (mouse_x, mouse_y)  # Save start point for shapes
    else:
        # Continue drawing
        if st.session_state.tool == "pen":
            draw.line(
                [st.session_state.last_point, (mouse_x, mouse_y)],
                fill=st.session_state.color,
                width=st.session_state.size
            )
            st.session_state.last_point = (mouse_x, mouse_y)
        elif st.session_state.tool == "eraser":
            draw.line(
                [st.session_state.last_point, (mouse_x, mouse_y)],
                fill="white",
                width=st.session_state.size
            )
            st.session_state.last_point = (mouse_x, mouse_y)
        
        # For shapes, we'll draw on mouse up
        st.session_state.last_point = (mouse_x, mouse_y)
    
    # Check if this was a mouse up event
    if st.session_state.get("mouse_up", False):
        if st.session_state.tool == "line" and st.session_state.start_point:
            draw.line(
                [st.session_state.start_point, (mouse_x, mouse_y)],
                fill=st.session_state.color,
                width=st.session_state.size
            )
        elif st.session_state.tool == "rectangle" and st.session_state.start_point:
            draw.rectangle(
                [st.session_state.start_point, (mouse_x, mouse_y)],
                outline=st.session_state.color,
                width=st.session_state.size
            )
        elif st.session_state.tool == "circle" and st.session_state.start_point:
            # Calculate radius based on distance from start point
            radius = ((mouse_x - st.session_state.start_point[0])**2 + 
                     (mouse_y - st.session_state.start_point[1])**2)**0.5
            draw.ellipse(
                [
                    st.session_state.start_point[0] - radius,
                    st.session_state.start_point[1] - radius,
                    st.session_state.start_point[0] + radius,
                    st.session_state.start_point[1] + radius
                ],
                outline=st.session_state.color,
                width=st.session_state.size
            )
        
        # Reset drawing state
        st.session_state.drawing = False
        st.session_state.last_point = None
        st.session_state.start_point = None
        st.session_state.mouse_up = False
    
    # Update the canvas in session state
    st.session_state.canvas = canvas
    
    # Update the displayed image
    img_bytes = io.BytesIO()
    st.session_state.canvas.save(img_bytes, format='PNG')
    img_data = img_bytes.getvalue()
    canvas_placeholder.image(img_data, use_container_width=True, caption="Draw on the canvas")
