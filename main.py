"""
from pyrogram import Client, filters
from database import *
from database import add_topup, get_topup, add_coin, get_coin

# Inisialisasi klien Pyrogram
api_id = "29855436"
api_hash = "c01b59b1d686c55d60a92c171e2b19fe"
bot_token = "6381483867:AAEAT3PbP7h5cejrgyb8e6wKP3gO0KshmvQ"

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# ID pengguna admin
ADMIN_ID = 1814359323  # Ganti dengan ID pengguna admin yang sesuai

# Simpan informasi top-up yang diminta oleh pengguna
topup_requests = {}
my_coin = {}

# Handler untuk perintah /start
@app.on_message(filters.command("start"))
def start_command(client, message):
    user_id = message.from_user.id
    client.send_message(message.chat.id, f"Halo! Selamat datang di bot top-up. Untuk melakukan top-up, silakan gunakan perintah /request_topup.")

# Handler untuk perintah /admin_topup
@app.on_message(filters.command("admin_topup") & filters.user(ADMIN_ID))
def admin_topup_command(client, message):
    if len(topup_requests) == 0:
        client.send_message(message.chat.id, "Tidak ada permintaan top-up yang tertunda saat ini.")
    else:
        for user_id, amount in topup_requests.items():
            # Lakukan logika untuk melakukan top-up
            # Misalnya, mengirimkan coin ke pengguna
            client.send_message(ADMIN_ID, f"Coin sejumlah {amount} telah dikirim ke pengguna dengan ID: {user_id}")
        topup_requests.clear()  # Bersihkan daftar permintaan top-up

# Handler untuk perintah /request_topup
@app.on_message(filters.command("request_topup"))
def request_topup_command(client, message):
    user_id = message.from_user.id
    amount = 100  # Contoh jumlah top-up yang diminta, ganti dengan logika yang sesuai

    # Tambahkan permintaan top-up ke daftar
    topup_requests[user_id] = amount

    client.send_message(message.chat.id, "Permintaan top-up telah diterima. Tunggu hingga admin memproses.")

# Handler untuk perintah /check_coin
@app.on_message(filters.command("check_coin"))
def check_coin_command(client, message):
    user_id = message.from_user.id
    coin_balance = my_coin.get(user_id, 0)
    client.send_message(message.chat.id, f"Saldo my coin Anda: {coin_balance}")


# Jalankan bot
print("AKTIF🔥")
app.run()
"""


import pymongo
import requests
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.types import Message

# Inisialisasi koneksi ke MongoDB
client = MongoClient("mongodb+srv://avel:tmp0@aveltmp.nqyqy6h.mongodb.net/aveltmp?retryWrites=true&w=majority")
db = client["bot_store"]
users_collection = db["users"]

# Inisialisasi koneksi ke Telegram menggunakan Pyrogram
api_id = 29855436  # Ganti dengan API ID Anda
api_hash = "c01b59b1d686c55d60a92c171e2b19fe"  # Ganti dengan API Hash Anda
bot_token = "6381483867:AAEAT3PbP7h5cejrgyb8e6wKP3gO0KshmvQ"

app = Client("bot_store_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)


# Command /start untuk menyambut pengguna
@app.on_message(filters.command("start", prefixes="/"))
async def start_command_handler(client: Client, message: Message):
    user_id = message.from_user.id
    username = message.from_user.username

    # Tambahkan pengguna baru ke database jika belum terdaftar
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        users_collection.insert_one({"user_id": user_id, "username": username, "coin": 0})

    await message.reply("Selamat datang di Bot Store! Ketik /my_coin untuk melihat jumlah coin Anda.")


# Command /my_coin untuk pengguna
@app.on_message(filters.command("my_coin", prefixes="/"))
async def my_coin_command_handler(client: Client, message: Message):
    user_id = message.from_user.id

    # Cek apakah pengguna sudah terdaftar di database
    user = users_collection.find_one({"user_id": user_id})
    if user:
        coin = user.get("coin", 0)
        await message.reply(f"Anda memiliki {coin} coin.")
    else:
        await message.reply("Anda belum terdaftar.")


# Command /transfer_coin hanya untuk admin
@app.on_message(filters.command("transfer_coin", prefixes="/"))
async def transfer_coin_command_handler(client: Client, message: Message):
    admin_id = 1814359323  # Ganti dengan ID admin Anda

    if message.from_user.id == admin_id:
        # Mendapatkan informasi jumlah coin dan ID pengguna dari pesan
        command_parts = message.text.split(" ")
        if len(command_parts) == 3:
            try:
                coin_amount = int(command_parts[1])
                user_id = int(command_parts[2])
            except ValueError:
                await message.reply("Format perintah tidak valid. Gunakan: /transfer_coin <jumlah_coin> <id_pengguna>")
                return

            # Cek apakah pengguna yang dituju ada di database
            user = users_collection.find_one({"user_id": user_id})
            if user:
                current_coin = user.get("coin", 0)
                new_coin = current_coin + coin_amount

                # Perbarui jumlah coin pengguna
                users_collection.update_one({"user_id": user_id}, {"$set": {"coin": new_coin}})
                await message.reply(f"Transfer {coin_amount} coin berhasil ke pengguna dengan ID {user_id}.")
            else:
                await message.reply("Pengguna dengan ID tersebut tidak ditemukan.")
        else:
            await message.reply("Format perintah tidak valid. Gunakan: /transfer_coin <jumlah_coin> <id_pengguna>")
    else:
        await message.reply("Anda tidak memiliki akses untuk melakukan transfer coin.")


# Command /topup_coin untuk melakukan top-up coin
@app.on_message(filters.command("topup_coin", prefixes="/"))
async def topup_coin_command_handler(client: Client, message: Message):
    user_id = message.from_user.id

    # Cek apakah ada foto dalam pesan
    if message.photo:
        # Mendapatkan informasi jumlah coin dari caption
        coin_amount = None
        if message.caption:
            caption_parts = message.caption.split(" ")
            if len(caption_parts) == 2 and caption_parts[0] == "/topup_coin":
                try:
                    coin_amount = int(caption_parts[1])
                except ValueError:
                    pass

        if coin_amount is not None:
            await send_log_message(f"Top-up request: Pengguna dengan ID {user_id} meminta top-up sebanyak {coin_amount} coin.", message.photo[-1].file_id)
            await message.reply("Permintaan top-up Anda telah dikirimkan. Tim kami akan segera menanggapi.")
        else:
            await message.reply("Format caption tidak valid. Gunakan: /topup_coin <jumlah_coin>")
    else:
        await message.reply("Anda harus mengirimkan foto bukti transaksi untuk melakukan top-up.")


async def send_log_message(text, photo_file_id):
    log_group_id = -1001613490589  # Ganti dengan ID grup log Anda
    # Mengirim pesan ke grup log dengan foto
    requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendPhoto?chat_id={log_group_id}&caption={text}&photo={photo_file_id}"
)

# Jalankan bot store
print("AKTIF 🔥") 
app.run()
