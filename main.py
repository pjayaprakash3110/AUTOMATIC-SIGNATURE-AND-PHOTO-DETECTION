import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from roboflow import Roboflow
import tempfile
import os
import io
import qrcode

# Initialize the Roboflow API client
rf = Roboflow(api_key="L9IZWDSxvti64yIi51dM")

def is_face_detected(image_path):
    # Face detection using Roboflow API
    project = rf.workspace().project("face-detection-nni6v")
    model = project.version(1).model

    response = model.predict(image_path, confidence=40, overlap=30).json()

    if 'predictions' in response and len(response['predictions']) > 0:
        return True
    else:
        raise Exception("No face detected in the profile photo. Please upload a photo with a clear face.")

def is_sign_detected(image_path):
    # Signature detection using Roboflow API
    project = rf.workspace().project("sign-b5igq")
    model = project.version(2).model

    response = model.predict(image_path, confidence=40, overlap=30).json()

    if 'predictions' in response and len(response['predictions']) > 0:
        return True
    else:
        raise Exception("No signature detected. Please upload a clear signature.")

def generate_admit_card(name, exam_name, exam_date, exam_time, dob, city, state, exam_center, profile_photo, signature):
    # Create a blank canvas for the admit card
    width, height = 800, 600
    admit_card = Image.new("RGB", (width, height), (255, 255, 255))
    
    # Add a decorative header
    header_font = ImageFont.truetype("arial.ttf", 36)
    draw = ImageDraw.Draw(admit_card)
    header_text = f"Admit Card for {exam_name}"
    header_width, header_height = draw.textsize(header_text, font=header_font)
    draw.text(((width - header_width) // 2, 20), header_text, font=header_font, fill=(0, 0, 0))
    
    # Add candidate's name with a stylish font
    name_font = ImageFont.truetype("arial.ttf", 24)
    name_text = f"Name: {name}"
    draw.text((50, 130), name_text, font=name_font, fill=(0, 0, 0))
    
    # Add exam date, time, and date of birth
    info_font = ImageFont.truetype("arial.ttf", 20)
    date_text = f"Exam Date: {exam_date.strftime('%B %d, %Y')}"
    time_text = f"Exam Time: {exam_time.strftime('%I:%M %p')}"
    dob_text = f"Date of Birth: {dob.strftime('%B %d, %Y')}"
    draw.text((50, 170), date_text, font=info_font, fill=(0, 0, 0))
    draw.text((50, 210), time_text, font=info_font, fill=(0, 0, 0))
    draw.text((50, 245), dob_text, font=info_font, fill=(0, 0, 0))
    
    # Add city, state, and exam center boxes
    box_font = ImageFont.truetype("arial.ttf", 20)
    city_text = f"City: {city}"
    state_text = f"State: {state}"
    exam_center_text = f"Exam Center: {exam_center}"
    draw.text((50, 282), city_text, font=box_font, fill=(0, 0, 0))
    draw.text((50, 312), state_text, font=box_font, fill=(0, 0, 0))
    draw.text((50, 342), exam_center_text, font=box_font, fill=(0, 0, 0))
    
    # Paste profile photo with a decorative frame
    frame = Image.new("RGB", (160, 160), (0, 0, 0))
    frame.paste(profile_photo.resize((150, 150)), (5, 5))
    admit_card.paste(frame, (width - 285, 120))
    
    # Add a decorative signature
    admit_card.paste(signature.resize((200, 80)), (width - 300, 480))
    
    # Generate QR code for exam center information
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f"Exam Center: {exam_center}\nCity: {city}\nState: {state}")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img = qr_img.resize((100, 100), Image.ANTIALIAS)
    admit_card.paste(qr_img, (50, height - 150))
    
    return admit_card

def main():
    
    st.markdown(
        """
        <h1 style='text-align: center;'>Admit Card Generator</h1>
        <style>
        h1 {
            color: #CD5C5C;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    name = st.text_input("**Enter your name**")
    exam_name = st.text_input("**Enter exam name**")
    dob = st.date_input("**Date of Birth**")
    exam_date = st.date_input("**Select exam date**")
    exam_time = st.time_input("**Select exam time**")
    city = st.text_input("**City**")
    state = st.text_input("**State**")
    exam_center = st.text_input("**Exam Center**")
    
    profile_photo = st.file_uploader("Upload Profile Photo", type=["jpg", "png"])
    signature = st.file_uploader("Upload Signature", type=["jpg", "png"])
    
    if st.button("Generate Admit Card"):
        try:
            if not (name and exam_name and exam_date and exam_time and dob and city and state and exam_center):
                raise Exception("Please fill in all the details to generate the admit card.")
            
            if not (profile_photo and signature):
                raise Exception("Please upload both profile photo and signature.")
            
            # Create temporary files for the uploaded images
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_profile_file, tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_signature_file:
                temp_profile_path = temp_profile_file.name
                temp_profile_file.write(profile_photo.read())

                temp_signature_path = temp_signature_file.name
                temp_signature_file.write(signature.read())
            
            # Check if a face is detected in the profile photo
            if not is_face_detected(temp_profile_path):
                raise Exception("No face detected in the profile photo. Please upload a photo with a clear face.")
            
            # Check if a signature is detected
            if not is_sign_detected(temp_signature_path):
                raise Exception("No signature detected. Please upload a clear signature.")
            
            # Convert the temporary paths to PIL Image objects
            profile_image = Image.open(temp_profile_path)
            signature_image = Image.open(temp_signature_path)

            # Generate the admit card image
            admit_card = generate_admit_card(name, exam_name, exam_date, exam_time, dob, city, state, exam_center, profile_image, signature_image)

            # Convert the PIL Image to bytes
            admit_card_bytes = io.BytesIO()
            admit_card.save(admit_card_bytes, format="PNG")
            admit_card_bytes.seek(0)

            # Display the admit card image
            st.image(admit_card, caption="Generated Admit Card", use_column_width=True)

            # Add a download link
            st.download_button(
                label="Download Admit Card",
                data=admit_card_bytes.read(),
                file_name="admit_card.png",
                mime="image/png"
            )
        
        except Exception as e:
            st.exception(str(e))

        finally:
            # Clean up temporary files
            os.remove(temp_profile_path)
            os.remove(temp_signature_path)

if __name__ == "__main__":
    main()
