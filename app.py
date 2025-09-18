import streamlit as st
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, CircleModuleDrawer, SquareModuleDrawer
from qrcode.image.styles.colorfills import SolidFillColorMask
from PIL import Image, ImageDraw
import io
import base64

def create_qr_code(data, logo=None, fill_color="black", back_color="white", 
                   border=4, box_size=10, error_correct=qrcode.constants.ERROR_CORRECT_M,
                   module_drawer="square"):
    """
    Create a QR code with customizable options
    """
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=error_correct,
        box_size=box_size,
        border=border,
    )
    
    qr.add_data(data)
    qr.make(fit=True)
    
    # Choose module drawer style
    drawer_map = {
        "square": SquareModuleDrawer(),
        "circle": CircleModuleDrawer(),
        "rounded": RoundedModuleDrawer()
    }
    
    # Create QR code image with style
    if module_drawer != "square":
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=drawer_map[module_drawer],
            fill_color=fill_color,
            back_color=back_color
        )
    else:
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
    
    # Add logo if provided
    if logo is not None:
        logo_img = logo.copy()
        
        # Calculate logo size (about 1/5 of QR code size)
        qr_width, qr_height = img.size
        logo_size = min(qr_width, qr_height) // 5
        
        # Resize logo
        logo_img = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        
        # Create a white background for the logo (optional padding)
        padding = 10
        logo_bg = Image.new('RGB', (logo_size + padding*2, logo_size + padding*2), back_color)
        logo_bg.paste(logo_img, (padding, padding))
        
        # Calculate position to center the logo
        logo_pos = ((qr_width - logo_bg.size[0]) // 2, (qr_height - logo_bg.size[1]) // 2)
        
        # Paste logo onto QR code
        img.paste(logo_bg, logo_pos)
    
    return img

def get_download_link(img, filename):
    """Generate a download link for the image"""
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    b64 = base64.b64encode(buffer.read()).decode()
    return f'<a href="data:image/png;base64,{b64}" download="{filename}">Download QR Code</a>'

def main():
    st.set_page_config(
        page_title="QR Code Generator",
        page_icon="📱",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    st.title("🔗 QR Code Generator")
    st.markdown("Generate custom QR codes from URLs with logo embedding and styling options")
    
    # Create two columns for input and preview
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 Configuration")
        
        # URL input
        url = st.text_input(
            "Enter URL or text:",
            placeholder="https://example.com",
            help="Enter the URL or text you want to encode"
        )
        
        # Logo upload
        st.subheader("🖼️ Logo Settings")
        uploaded_logo = st.file_uploader(
            "Upload logo image (optional)",
            type=['png', 'jpg', 'jpeg'],
            help="Upload a logo to display in the center of the QR code"
        )
        
        # Styling options
        st.subheader("🎨 Styling Options")
        
        col_a, col_b = st.columns(2)
        with col_a:
            fill_color = st.color_picker("QR Code Color", "#000000")
            error_correction = st.selectbox(
                "Error Correction Level",
                options=[
                    qrcode.constants.ERROR_CORRECT_L,
                    qrcode.constants.ERROR_CORRECT_M,
                    qrcode.constants.ERROR_CORRECT_Q,
                    qrcode.constants.ERROR_CORRECT_H
                ],
                format_func=lambda x: {
                    qrcode.constants.ERROR_CORRECT_L: "Low (~7%)",
                    qrcode.constants.ERROR_CORRECT_M: "Medium (~15%)",
                    qrcode.constants.ERROR_CORRECT_Q: "Quartile (~25%)",
                    qrcode.constants.ERROR_CORRECT_H: "High (~30%)"
                }[x],
                index=1,
                help="Higher error correction allows for more logo coverage"
            )
        
        with col_b:
            back_color = st.color_picker("Background Color", "#FFFFFF")
            module_style = st.selectbox(
                "Module Style",
                options=["square", "circle", "rounded"],
                help="Choose the shape of QR code modules"
            )
        
        # Size options
        st.subheader("📏 Size Options")
        col_c, col_d = st.columns(2)
        with col_c:
            box_size = st.slider("Box Size", min_value=5, max_value=20, value=10)
        with col_d:
            border = st.slider("Border Size", min_value=1, max_value=10, value=4)
    
    with col2:
        st.header("👀 Preview")
        
        if url:
            try:
                # Process uploaded logo
                logo_img = None
                if uploaded_logo is not None:
                    logo_img = Image.open(uploaded_logo)
                    # Convert to RGB if necessary
                    if logo_img.mode in ("RGBA", "P"):
                        logo_img = logo_img.convert("RGB")
                
                # Generate QR code
                qr_img = create_qr_code(
                    data=url,
                    logo=logo_img,
                    fill_color=fill_color,
                    back_color=back_color,
                    border=border,
                    box_size=box_size,
                    error_correct=error_correction,
                    module_drawer=module_style
                )
                
                # Display QR code
                st.image(qr_img, caption="Generated QR Code", use_column_width=True)
                
                # Download button
                buffer = io.BytesIO()
                qr_img.save(buffer, format='PNG')
                st.download_button(
                    label="📥 Download QR Code",
                    data=buffer.getvalue(),
                    file_name=f"qrcode_{hash(url)}.png",
                    mime="image/png"
                )
                
                # QR code info
                st.info(f"QR Code generated for: {url[:50]}{'...' if len(url) > 50 else ''}")
                
            except Exception as e:
                st.error(f"Error generating QR code: {str(e)}")
        else:
            st.info("👆 Enter a URL above to generate QR code")
            
            # Show example QR code
            example_qr = create_qr_code("https://streamlit.io")
            st.image(example_qr, caption="Example QR Code", use_column_width=True, alpha=0.5)
    
    # Instructions
    st.markdown("---")
    with st.expander("ℹ️ Instructions"):
        st.markdown("""
        **How to use:**
        1. Enter the URL or text you want to encode
        2. Optionally upload a logo image (PNG/JPG)
        3. Customize colors, style, and size
        4. Download your custom QR code
        
        **Tips:**
        - Use higher error correction levels when adding logos
        - Keep logos simple and high contrast for best results
        - Test your QR code with different scanning apps
        - Ensure sufficient contrast between QR code and background colors
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("Made with ❤️ using Streamlit | [Source Code](https://github.com/yourusername/qr-code-generator)")

if __name__ == "__main__":
    main()