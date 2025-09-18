import streamlit as st
import qrcode
from PIL import Image
import io

# --- Page Config ---
st.set_page_config(page_title="makeQRs", page_icon="🔗", layout="centered")

# --- Header ---
st.markdown(
    """
    <h1 style='text-align: center; color: #2E86C1;'>🔗 QR Code Generator</h1>
    <p style='text-align: center; color: gray;'>
        Enter any link or text below to generate a clean, downloadable QR Code instantly.
    </p>
    """,
    unsafe_allow_html=True
)

# --- Input Section ---
link = st.text_input("Enter a URL or text:", placeholder="e.g., https://example.com")

if link.strip():
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )
    qr.add_data(link)
    qr.make(fit=True)

    # Convert QR to PIL image
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    # Save image to bytes buffer
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()

    # --- Display Section ---
    st.markdown("### 📷 Preview")
    st.image(byte_im, caption="Your QR Code", use_container_width=False)

    # --- Download Button ---
    st.download_button(
        label="📥 Download QR Code",
        data=byte_im,
        file_name="qrcode.png",
        mime="image/png"
    )

# --- Footer ---
st.markdown(
    """
    <hr>
    <p style='text-align: center; color: gray; font-size: 14px;'>
        Built by <b>asv</b>
    </p>
    """,
    unsafe_allow_html=True
)
