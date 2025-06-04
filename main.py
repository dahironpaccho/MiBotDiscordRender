import discord
from discord.ext import commands
from discord import app_commands
import os
from keep_alive import keep_alive  # ¡Añade esta línea!

# --- Configuración de Intenciones (Intents) ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# --- Inicialización del Bot ---
bot = commands.Bot(command_prefix="!", intents=intents)

# --- IDs Importantes de tu Servidor ---
ROL_ID = 1378868459101753418
CANAL_REGLAS_ID = 1378800039941505346
CANAL_ANUNCIOS_GENERAL_ID = 1378805324080746638
CANALES_TEXTO_PLANO_BOLD_IDS = [
    1378807979943661568,
    1378798993466855596,
    1378807446705012808,
    1378808142346981376,
    1378809007720104077,
    1379219273796288603,
    1379219419607072943
]
CANAL_ANUNCIOS_ROBUX_ID = 1379229048487677972
ROL_ANUNCIO_PERMITIDO_ID = 1378977225776304169

# --- Evento: Cuando el Bot Está Listo ---
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    await enviar_reglas()
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} comandos sincronizados")
    except Exception as e:
        print(f"❌ Error sincronizando comandos: {e}")

# --- Función Auxiliar: Enviar Reglas ---
async def enviar_reglas():
    canal = bot.get_channel(CANAL_REGLAS_ID)
    if canal is None:
        print("❌ Canal de reglas no encontrado. Verifica CANAL_REGLAS_ID.")
        return

    async for mensaje in canal.history(limit=10):
        if mensaje.author == bot.user and mensaje.embeds and "Bienvenidos al servidor oficial" in mensaje.embeds[0].title:
            print("ℹ️ Mensaje de reglas ya existe. No se enviará de nuevo.")
            return

    embed = discord.Embed(
        title="🎉¡Bienvenidos al servidor oficial de Dibujitos Al Ataque!🎉",
        description=(
            "**Normas de Convivencia (¡Sé un buen dibujito!)**\n\n"
            "**Usa los canales para lo que son:**\n"
            "Cada espacio tiene su propósito. Publica tus mensajes donde corresponda.\n\n"
            "**¡Cero contenido inapropiado!**\n"
            "Nada de cosas +18 o violentas.\n\n"
            "**¡No al spam!**\n"
            "Evita repetir mensajes o enviar publicidad no solicitada.\n\n"
            "**¿Ves algo raro?**\n"
            "¡Reporta! Ayúdanos a mantener la comunidad sana.\n\n"
            "**¿Dudas?**\n"
            "Pregunta con respeto.\n\n"
            "*Haz clic en el botón de abajo para aceptar las reglas y unirte a la pandilla 👇*"
        ),
        color=discord.Color.blue()
    )
    embed.set_footer(text="Gracias por formar parte de la comunidad 💙 by: pablito")

    view = BotonRolView()
    await canal.send(embed=embed, view=view)

# --- Clase para Botón de Reglas ---
class BotonRolView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="¡Aceptar Reglas y Unirme!", style=discord.ButtonStyle.success, custom_id="aceptar_reglas")
    async def aceptar(self, interaction: discord.Interaction, button: discord.ui.Button):
        rol = interaction.guild.get_role(ROL_ID)
        if rol in interaction.user.roles:
            await interaction.response.send_message("¡Ya tienes el rol, dibujito!", ephemeral=True)
        else:
            await interaction.user.add_roles(rol)
            await interaction.response.send_message("🎉 ¡Rol asignado! Bienvenido a la pandilla 🎨", ephemeral=True)

# --- Slash Command: /anuncio ---
@bot.tree.command(name="anuncio", description="Envía un anuncio con formato especial o general.")
@app_commands.describe(mensaje="El contenido del anuncio.")
@app_commands.checks.has_role(ROL_ANUNCIO_PERMITIDO_ID) # <-- ¡ESTE ES EL CAMBIO SOLUCIONADO!
async def anuncio(interaction: discord.Interaction, mensaje: str):
    try:
        canal_de_ejecucion_id = interaction.channel_id
        canal_destino = None

        if canal_de_ejecucion_id == CANAL_ANUNCIOS_GENERAL_ID:
            canal_destino = bot.get_channel(CANAL_ANUNCIOS_GENERAL_ID)
            formato_especial = False
        elif canal_de_ejecucion_id == CANAL_ANUNCIOS_ROBUX_ID:
            canal_destino = bot.get_channel(CANAL_ANUNCIOS_ROBUX_ID)
            formato_especial = False
        elif canal_de_ejecucion_id in CANALES_TEXTO_PLANO_BOLD_IDS:
            canal_destino = bot.get_channel(canal_de_ejecucion_id)
            formato_especial = True
        else:
            canal_destino = bot.get_channel(CANAL_ANUNCIOS_GENERAL_ID)
            formato_especial = False

        if canal_destino is None:
            await interaction.response.send_message("❌ No se encontró el canal de destino para el anuncio.", ephemeral=True)
            return

        if formato_especial:
            await canal_destino.send(f"**{mensaje}**")
        else:
            embed = discord.Embed(
                title="📢 Anuncio Oficial",
                description=mensaje,
                color=discord.Color.blue()
            )
            await canal_destino.send(embed=embed)

        await interaction.response.send_message(f"✅ ¡Anuncio enviado con éxito a {canal_destino.mention}!", ephemeral=True)

    except Exception as e:
        print(f"❌ Error en el comando /anuncio: {e}")
        await interaction.response.send_message("❌ Hubo un error al intentar enviar el anuncio.", ephemeral=True)

# --- Manejo de Errores ---
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingRole):
        await interaction.response.send_message(f"❌ ¡Lo siento, {interaction.user.mention}! No tienes el rol necesario para usar este comando.", ephemeral=True)
    else:
        print(f"❌ Error en un comando de barra diagonal: {error}")
        await interaction.response.send_message("❌ Hubo un error al ejecutar este comando.", ephemeral=True)

# --- Ejecución del Bot ---
keep_alive()  # Asegura que el bot se mantenga activo (Replit u hosting similar)
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
