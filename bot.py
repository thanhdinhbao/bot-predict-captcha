import cv2
import numpy as np
import tensorflow as tf
import string
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackContext

# Cấu hình bot
TOKEN = "7189002188:AAEr9KZ_lZ0YutWGzfbyI9GMDyu811HIOoQ"  # Thay bằng token của bạn

# Load model CAPTCHA
model = tf.keras.models.load_model("captcha_model.h5")

# Danh sách ký tự CAPTCHA
CHARS = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
IMG_WIDTH, IMG_HEIGHT = 128, 64

def label_to_text(labels):
    text = ""
    for lbl in labels:
        if lbl < 10:
            text += chr(lbl + ord('0'))
        elif lbl < 36:
            text += chr(lbl - 10 + ord('A'))
        else:
            text += chr(lbl - 36 + ord('a'))
    return text

def predict_captcha(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT))
    img = img / 255.0
    img = img.reshape(1, IMG_HEIGHT, IMG_WIDTH, 1)

    preds = model.predict(img)
    pred_labels = [np.argmax(pred) for pred in preds]
    return label_to_text(pred_labels)

async def handle_photo(update: Update, context: CallbackContext):
    photo = update.message.photo[-1]  # Lấy ảnh có độ phân giải cao nhất
    file = await context.bot.get_file(photo.file_id)

    file_path = "temp_captcha.png"
    await file.download_to_drive(file_path)

    predicted_text = predict_captcha(file_path)

    await update.message.reply_text(f"Dự đoán CAPTCHA: {predicted_text}")

    os.remove(file_path)  # Xóa file tạm sau khi xử lý xong

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Gửi ảnh CAPTCHA để tôi nhận diện!")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
