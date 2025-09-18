import streamlit as st
import qrcode
from PIL import Image, ImageDraw, ImageFont
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
col_controls, col_preview = st.columns([1, 1.2])

with col_controls:
    # --- User Input ---
    link = st.text_area("Enter URL or text:", placeholder="https://example.com", height=80)

    # --- QR Settings ---
    with st.expander("QR Settings"):
        fill_color = st.color_picker("QR Foreground Color", "#000000")
        back_color = st.color_picker("QR Background Color", "#FFFFFF")
        border = st.slider("Border Size", 1, 10, 3)
        qr_size = 600  # fixed resolution

    # --- Center Text ---
    with st.expander("Center Text"):
        center_text = st.text_input("Text in Center", placeholder="Your Company Name")
        text_percent = st.slider("Text Size (% of QR width)", 5, 50, 10)
        text_color = st.color_picker("Text Color", "#000000")
        text_bg_padding = st.slider("Background Padding", 0, 30, 5)
        show_text_bg = st.checkbox("Show Text Background", True)

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

        logo_percent = st.slider("Logo Size (% of QR width)", 10, 40, 20)
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
                center_text, text_percent, text_color, text_bg_padding, show_text_bg,
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

    # --- Add Center Text ---
    if center_text.strip():
        draw = ImageDraw.Draw(img)
        try:
            font_size = int(qr_size * text_percent / 100)
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), center_text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_pos = ((qr_size - text_w) // 2, (qr_size - text_h) // 2)

        if show_text_bg:
            rect_coords = [
                text_pos[0] - text_bg_padding,
                text_pos[1] - text_bg_padding,
                text_pos[0] + text_w + text_bg_padding,
                text_pos[1] + text_h + text_bg_padding
            ]
            draw.rectangle(rect_coords, fill=back_color)

        draw.text(text_pos, center_text, fill=text_color, font=font)

    return img

# --- Generate QR ---
if generate_btn:
    if link.strip():
        try:
            img = generate_qr(
                link, fill_color, back_color, border,
                center_text, text_percent, text_color, text_bg_padding, show_text_bg,
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
