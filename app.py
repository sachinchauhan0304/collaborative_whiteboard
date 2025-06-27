# app.py - CollabDraw Streamlit Version
import streamlit as st
from PIL import Image, ImageDraw
import io
import numpy as np

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
if 'start_point' not in st.session_state:
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

# Create a canvas placeholder
canvas_placeholder = st.empty()

# Display the current canvas
def display_canvas():
    img_bytes = io.BytesIO()
    st.session_state.canvas.save(img_bytes, format='PNG')
    canvas_placeholder.image(img_bytes.getvalue(), use_container_width=True, caption="Draw on the canvas")

display_canvas()

# Mouse event handling using st.file_uploader workaround
uploaded_file = st.file_uploader("", type=["png"], label_visibility="collapsed")
if uploaded_file is not None:
    # Get mouse coordinates from the file name (workaround)
    try:
        coords = uploaded_file.name.split("_")[-1].split(".")[0].split("-")
        x, y = float(coords[0]), float(coords[1])
        action = "drag" if len(coords) > 2 else "click"
        
        # Create a new drawing context
        canvas = st.session_state.canvas.copy()
        draw = ImageDraw.Draw(canvas)
        
        if action == "click":
            # Handle mouse down
            st.session_state.drawing = True
            st.session_state.start_point = (x, y)
            st.session_state.last_point = (x, y)
            
            if st.session_state.tool == "pen":
                draw.ellipse(
                    [(x-st.session_state.size, y-st.session_state.size),
                     (x+st.session_state.size, y+st.session_state.size)],
                    fill=st.session_state.color
                )
            elif st.session_state.tool == "eraser":
                draw.ellipse(
                    [(x-st.session_state.size, y-st.session_state.size),
                     (x+st.session_state.size, y+st.session_state.size)],
                    fill="white"
                )
        else:
            # Handle mouse move/drag
            if st.session_state.drawing and st.session_state.last_point:
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
                
                st.session_state.last_point = (x, y)
        
        st.session_state.canvas = canvas
        display_canvas()
        
    except:
        pass

# JavaScript for mouse tracking
st.markdown("""
<script>
// Create a transparent canvas overlay
const img = document.querySelector('.stImage img');
if (img) {
    const overlay = document.createElement('canvas');
    overlay.style.position = 'absolute';
    overlay.style.left = img.offsetLeft + 'px';
    overlay.style.top = img.offsetTop + 'px';
    overlay.width = img.width;
    overlay.height = img.height;
    overlay.style.pointerEvents = 'auto';
    overlay.style.cursor = 'crosshair';
    img.parentNode.insertBefore(overlay, img.nextSibling);
    
    // Track mouse events
    overlay.onmousedown = (e) => {
        const x = e.offsetX * (img.naturalWidth / img.width);
        const y = e.offsetY * (img.naturalHeight / img.height);
        const fakeFile = new File([""], `draw_${x}-${y}.png`);
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(fakeFile);
        const fileInput = document.querySelector('input[type="file"]');
        fileInput.files = dataTransfer.files;
        fileInput.dispatchEvent(new Event('change', { bubbles: true }));
    };
    
    overlay.onmousemove = (e) => {
        if (e.buttons === 1) {  // Left button pressed
            const x = e.offsetX * (img.naturalWidth / img.width);
            const y = e.offsetY * (img.naturalHeight / img.height);
            const fakeFile = new File([""], `draw_${x}-${y}-drag.png`);
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(fakeFile);
            const fileInput = document.querySelector('input[type="file"]');
            fileInput.files = dataTransfer.files;
            fileInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
    };
    
    overlay.onmouseup = (e) => {
        const x = e.offsetX * (img.naturalWidth / img.width);
        const y = e.offsetY * (img.naturalHeight / img.height);
        
        // Handle shape drawing on mouse up
        const fakeFile = new File([""], `draw_${x}-${y}-shape.png`);
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(fakeFile);
        const fileInput = document.querySelector('input[type="file"]');
        fileInput.files = dataTransfer.files;
        fileInput.dispatchEvent(new Event('change', { bubbles: true }));
    };
}
</script>
""", unsafe_allow_html=True)

# Handle shape drawing on mouse up
if st.session_state.get('drawing', False) and st.session_state.start_point:
    # Get the latest canvas
    canvas = st.session_state.canvas.copy()
    draw = ImageDraw.Draw(canvas)
    
    # Check if we should draw a shape
    if st.session_state.tool in ["rectangle", "circle", "line"]:
        # Get the end point (use last_point if available)
        end_point = st.session_state.last_point if st.session_state.last_point else st.session_state.start_point
        
        if st.session_state.tool == "rectangle":
            draw.rectangle(
                [st.session_state.start_point, end_point],
                outline=st.session_state.color,
                width=st.session_state.size
            )
        elif st.session_state.tool == "circle":
            # Calculate radius based on distance
            radius = ((end_point[0] - st.session_state.start_point[0])**2 + 
                     (end_point[1] - st.session_state.start_point[1])**2)**0.5
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
        elif st.session_state.tool == "line":
            draw.line(
                [st.session_state.start_point, end_point],
                fill=st.session_state.color,
                width=st.session_state.size
            )
        
        st.session_state.canvas = canvas
        display_canvas()
    
    # Reset drawing state
    st.session_state.drawing = False
    st.session_state.start_point = None
    st.session_state.last_point = None
