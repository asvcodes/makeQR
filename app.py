import streamlit as st
import qrcode
from PIL import Image, ImageDraw
import io
from streamlit_cropper import st_cropper

# --- Page Config ---
st.set_page_config(page_title="makeQR", layout="wide")

# --- Header ---
st.markdown(
    """
    <h1 style='text-align: center; color: #2E86C1;'>makeQRs</h1>
    <p style='text-align: center; color: gray;'>Generate customizable QR codes without any ads... </p>
    """,
    unsafe_allow_html=True
)

# --- Layout ---
col_controls, col_preview = st.columns([1.3, 1])  # give controls more width

with col_controls:
    # --- User Input ---
    link = st.text_area("Enter URL or text:", placeholder="https://example.com", height=80)

    # --- QR Settings ---
    with st.expander("QR Settings"):
        fill_color = st.color_picker("QR Foreground Color", "#000000")
        back_color = st.color_picker("QR Background Color", "#FFFFFF")
        border = st.slider("Border Size", 1, 10, 3)
        qr_size = 600  # fixed resolution

    # --- Logo Options ---
    with st.expander("Logo"):
        logo_file = st.file_uploader("Upload Logo/Image", type=["png", "jpg", "jpeg"])
        if logo_file:
            image = Image.open(logo_file).convert("RGBA")
            st.markdown("**Crop your logo before embedding**")
            cropped_image = st_cropper(
                image,
                realtime_update=True,
                box_color="#2E86C1",
                aspect_ratio=None,
                return_type="image"
            )
        else:
            cropped_image = None

        logo_percent = st.slider("Logo Size", 10, 40, 20)
        round_logo = st.checkbox("Round Logo?", False)

    generate_btn = st.button("Generate QR Code")

# --- Preview Placeholder ---
with col_preview:
    qr_placeholder = st.empty()
    qr_placeholder.image(
        Image.new("RGBA", (qr_size, qr_size), color="#D3D3D3"),
        caption="QR Preview",
        use_container_width=True
    )

# --- QR Generation Function ---
def generate_qr(link, fill_color, back_color, border,
                logo_img, logo_percent, round_logo, qr_size=600):

    # --- Create QR ---
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,  # fixed
        border=border
    )
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGBA")
    img = img.resize((qr_size, qr_size), Image.LANCZOS)

    # --- Add Logo ---
    if logo_img:
        logo_size = int(qr_size * logo_percent / 100)
        logo = logo_img.resize((logo_size, logo_size), Image.LANCZOS)

        if round_logo:
            mask = Image.new("L", logo.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, logo.size[0], logo.size[1]), fill=255)
            logo.putalpha(mask)

        pos = ((qr_size - logo.size[0]) // 2, (qr_size - logo.size[1]) // 2)
        img.paste(logo, pos, mask=logo)

    return img

# --- Generate QR ---
if generate_btn:
    if link.strip():
        try:
            img = generate_qr(
                link, fill_color, back_color, border,
                cropped_image, logo_percent, round_logo, qr_size
            )
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            qr_placeholder.image(buf.getvalue(), caption="Generated QR Code", use_container_width=True)

            st.download_button(
                label="Download QR",
                data=buf.getvalue(),
                file_name="qrcode.png",
                mime="image/png"
            )
        except Exception as e:
            st.error(f"Error generating QR code: {e}")
    else:
        st.warning("Enter a URL or text to generate the QR code.")

# --- Footer ---
st.markdown(
    "<hr><p style='text-align:center; color:gray;'>Built by ASV</p>",
    unsafe_allow_html=True
)