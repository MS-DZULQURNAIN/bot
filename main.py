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
