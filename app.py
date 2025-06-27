import streamlit as st
from streamlit_drawable_canvas import st_canvas

# Set page config
st.set_page_config(
    page_title="CollabDraw",
    page_icon=":pencil2:",
    layout="wide"
)

# Initialize session state
if 'tool' not in st.session_state:
    st.session_state.tool = "freedraw"
if 'color' not in st.session_state:
    st.session_state.color = "#000000"
if 'size' not in st.session_state:
    st.session_state.size = 5
if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#FFFFFF"
if 'canvas_key' not in st.session_state:
    st.session_state.canvas_key = "default_canvas"

# Custom CSS to make canvas responsive
st.markdown("""
<style>
    .stCanvas {
        border: 1px solid #ddd;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Tools panel
with st.sidebar:
    st.title("🖌️ Drawing Tools")
    
    st.session_state.tool = st.radio(
        "Select Tool:",
        ["freedraw", "line", "rect", "circle", "transform"],
        format_func=lambda x: {
            "freedraw": "✏️ Pen",
            "line": "📏 Line", 
            "rect": "🟦 Rectangle",
            "circle": "⭕ Circle",
            "transform": "✋ Select/Move"
        }[x]
    )
    
    st.session_state.color = st.color_picker("Choose Color:", st.session_state.color)
    st.session_state.size = st.slider("Brush Size:", 1, 30, st.session_state.size)
    st.session_state.bg_color = st.color_picker("Canvas Color:", st.session_state.bg_color)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧹 Clear Canvas", use_container_width=True):
            st.session_state.canvas_key = str(hash("new_canvas"))
            st.rerun()
    with col2:
        if st.button("💾 Save Canvas", use_container_width=True):
            pass  # Handled below

# Main app area
st.title("🎨 CollabDraw - Collaborative Whiteboard")
st.markdown("Draw together in real-time!")

# Drawing canvas
canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 0.3)",  # Transparent fill
    stroke_width=st.session_state.size,
    stroke_color=st.session_state.color,
    background_color=st.session_state.bg_color,
    height=600,
    width=800,
    drawing_mode=st.session_state.tool,
    point_display_radius=0,
    key=f"canvas_{st.session_state.canvas_key}",
    display_toolbar=False,
    update_streamlit=True
)

# Save functionality
if st.session_state.get('save_triggered', False):
    if canvas_result.image_data is not None:
        st.download_button(
            label="⬇️ Download Drawing",
            data=canvas_result.image_data,
            file_name="collabdraw.png",
            mime="image/png",
            use_container_width=True
        )
    st.session_state.save_triggered = False

# Handle the save button from sidebar
if st.session_state.get('save_clicked', False):
    st.session_state.save_triggered = True
    st.session_state.save_clicked = False
    st.rerun()

# Instructions
with st.expander("ℹ️ How to use"):
    st.markdown("""
    - **Pen**: Freehand drawing
    - **Line**: Click and drag to draw straight lines
    - **Rectangle**: Click and drag to draw rectangles
    - **Circle**: Click and drag to draw ellipses
    - **Select/Move**: Click and drag to move objects
    - Use the sidebar to change colors and brush size
    - Click 'Clear Canvas' to start over
    - Click 'Save Canvas' to download your drawing
    """)

# Add some spacing
st.markdown("<br><br>", unsafe_allow_html=True)
