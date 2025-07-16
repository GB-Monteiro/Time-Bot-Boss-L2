import discord
import asyncio
from datetime import datetime, timedelta, timezone
import json
import os
from flask import Flask
from threading import Thread

# ========== Timezone Config ==========
UTC_MINUS_3 = timezone(timedelta(hours=-3))

# ========== Configuração do Flask (Keep Alive) ==========
app = Flask('')


@app.route('/')
def home():
    return "I'm alive!"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()


# ========== Configuração do Bot ==========
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Coloque aqui o ID do canal onde deseja receber alertas
ALERTA_CANAL_ID = 1388993724213756004  # 🔴 Substitua com o ID real do canal de alertas

bosses = {
    "queen ant": {"min": 21, "max": 23},
    "core": {"min": 20, "max": 24},
    "orfen": {"min": 18, "max": 26},
    "zaken": {"min": 16, "max": 28},
}

DATA_FILE = "boss_data.json"


def carregar_dados():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}


def salvar_dados(dados):
    with open(DATA_FILE, "w") as f:
        json.dump(dados, f, indent=4)


dados_boss = carregar_dados()


@client.event
async def on_ready():
    print(f'Bot connected as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    conteudo = message.content.lower()

    if conteudo.startswith("!boss died"):
        partes = conteudo.split(" ", 2)
        if len(partes) < 3:
            await message.channel.send("Use: `!boss died <boss>`")
            return

        nome_boss = partes[2].lower()
        if nome_boss not in bosses:
            await message.channel.send("Invalid boss. Use `!listbosses` to view bosses.")
            return

        hora_morte = datetime.now(UTC_MINUS_3).strftime("%Y-%m-%d %H:%M:%S")
        dados_boss[nome_boss] = hora_morte
        salvar_dados(dados_boss)

        await message.channel.send(f'{nome_boss.title()} died at {hora_morte} (GMT-3).')

        hora_morte_dt = datetime.strptime(hora_morte, "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC_MINUS_3)
        inicio_respawn = hora_morte_dt + timedelta(hours=bosses[nome_boss]["min"])
        fim_respawn = hora_morte_dt + timedelta(hours=bosses[nome_boss]["max"])

        segundos_ate_inicio = (inicio_respawn - datetime.now(UTC_MINUS_3)).total_seconds()
        segundos_ate_fim = (fim_respawn - datetime.now(UTC_MINUS_3)).total_seconds()

        await asyncio.sleep(max(0, segundos_ate_inicio))

        canal_alerta = client.get_channel(ALERTA_CANAL_ID)
        if canal_alerta:
            await canal_alerta.send(
                f'@everyone {nome_boss.title()} started random respawn now at ({inicio_respawn.strftime("%H:%Mh (GMT-3)")}) '
                f'and ends at ({fim_respawn.strftime("%H:%Mh (GMT-3)")})'
            )
        else:
            await message.channel.send("⚠️ Alert channel not found. Check ALERTA_CANAL_ID.")

        await asyncio.sleep(max(0, segundos_ate_fim - segundos_ate_inicio))

        if nome_boss in dados_boss:
            dados_boss.pop(nome_boss)
            salvar_dados(dados_boss)
            if canal_alerta:
                await canal_alerta.send(f"📤 {nome_boss.title()} has been removed from the status list (respawn window ended).")

    elif conteudo.startswith("!bossstatus"):
        resposta = "📋 Boss Status:\n"
        for boss in bosses:
            if boss in dados_boss:
                hora_morte = datetime.strptime(dados_boss[boss], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC_MINUS_3)
                inicio_respawn = hora_morte + timedelta(hours=bosses[boss]["min"])
                fim_respawn = hora_morte + timedelta(hours=bosses[boss]["max"])
                resposta += (
                    f"- {boss.title()}: Dead at {hora_morte.strftime('%d/%m %H:%Mh (GMT-3)')} | "
                    f"Respawn: {inicio_respawn.strftime('%d/%m %H:%Mh (GMT-3)')} → {fim_respawn.strftime('%d/%m %H:%Mh (GMT-3)')}\n"
                )
            else:
                resposta += f"- {boss.title()}: No registration.\n"
        await message.channel.send(resposta)

    elif conteudo.startswith("!cancelboss"):
        partes = conteudo.split(" ", 1)
        if len(partes) < 2:
            await message.channel.send("Use: `!cancelboss <boss>`")
            return

        nome_boss = partes[1].lower()
        if nome_boss in dados_boss:
            dados_boss.pop(nome_boss)
            salvar_dados(dados_boss)
            await message.channel.send(f"Boss log {nome_boss.title()} removed.")
        else:
            await message.channel.send("This boss has no active record.")

    elif conteudo.startswith("!setboss"):
        partes = conteudo.split(" ")
        if len(partes) < 3:
            await message.channel.send("Use: `!setboss <boss> <time in the format HH:MM (GMT-3)>`")
            return

        nome_boss = partes[1].lower()
        hora_digitada = partes[2]

        boss_correspondente = None
        for boss in bosses:
            if nome_boss == boss or nome_boss.replace(" ", "") == boss.replace(" ", ""):
                boss_correspondente = boss
                break

        if boss_correspondente is None:
            await message.channel.send("Invalid boss.")
            return

        try:
            agora = datetime.now(UTC_MINUS_3)
            hora_morte = agora.replace(
                hour=int(hora_digitada.split(":")[0]),
                minute=int(hora_digitada.split(":")[1]),
                second=0,
                microsecond=0
            )
        except ValueError:
            await message.channel.send("Invalid time. Use format HH:MM (e.g: 18:30).")
            return

        dados_boss[boss_correspondente] = hora_morte.strftime("%Y-%m-%d %H:%M:%S")
        salvar_dados(dados_boss)

        await message.channel.send(
            f"Boss death time {boss_correspondente.title()} manually adjusted to {hora_morte.strftime('%H:%Mh (GMT-3)')}."
        )

    elif conteudo.startswith("!nextrespawn"):
        proximo_boss = None
        menor_tempo = None

        for boss in bosses:
            if boss in dados_boss:
                hora_morte = datetime.strptime(dados_boss[boss], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC_MINUS_3)
                inicio_respawn = hora_morte + timedelta(hours=bosses[boss]["min"])
                tempo_ate_inicio = (inicio_respawn - datetime.now(UTC_MINUS_3)).total_seconds()

                if tempo_ate_inicio > 0:
                    if menor_tempo is None or tempo_ate_inicio < menor_tempo:
                        menor_tempo = tempo_ate_inicio
                        proximo_boss = (boss, inicio_respawn)

        if proximo_boss:
            await message.channel.send(
                f"⏰ Next respawn: {proximo_boss[0].title()} random respawn will begin at {proximo_boss[1].strftime('%H:%Mh (GMT-3)')}."
            )
        else:
            await message.channel.send("No bosses with nearby respawns.")

    elif conteudo.startswith("!listbosses"):
        lista = "\n".join([f"- {boss.title()}" for boss in bosses])
        await message.channel.send(f"📜 Available bosses:\n{lista}")


# ========== Iniciar Keep Alive + Bot ==========
keep_alive()
client.run(TOKEN)
