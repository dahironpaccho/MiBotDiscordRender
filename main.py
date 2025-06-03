import discord
from discord.ext import commands
from discord import app_commands
import os
from keep_alive import keep_alive # ¡Añade esta línea!

# --- Configuración de Intenciones (Intents) ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# --- Inicialización del Bot ---
bot = commands.Bot(command_prefix="!", intents=intents)

# --- IDs Importantes de tu Servidor (¡ACTUALIZA ESTOS VALORES!) ---
# Asegúrate de que estos IDs sean los correctos de tu servidor de Discord.
# Para obtener un ID: activa el Modo Desarrollador en Discord (Ajustes de Usuario > Comportamiento),
# luego haz clic derecho en el rol/canal y selecciona "Copiar ID".
ROL_ID = 1378868459101753418  # ID del rol que se asignará al aceptar las reglas
CANAL_REGLAS_ID = 1378800039941505346 # ID del canal donde se enviarán las reglas

# ID del canal de anuncios GENERAL donde se envía el embed completo
CANAL_ANUNCIOS_GENERAL_ID = 1378805324080746638

# IDs de canales donde el mensaje debe ser SOLO texto en negrita y sin embed
CANALES_TEXTO_PLANO_BOLD_IDS = [
    1378807979943661568, # Ejemplo: canal_id_1
    1378798993466855596, # Ejemplo: canal_id_2
    1378807446705012808, # Ejemplo: canal_id_3
    1378808142346981376, # Ejemplo: canal_id_4
    1378809007720104077, # Ejemplo: canal_id_5
    1379219273796288603, # Ejemplo: canal_id_6
    1379219419607072943  # Ejemplo: canal_id_7
]

# ID del canal específico de Robux que mencionaste, donde quieres que funcione el anuncio directamente
CANAL_ANUNCIOS_ROBUX_ID = 1379229048487677972

# ¡NUEVO! ID del rol permitido para usar el comando /anuncio
ROL_ANUNCIO_PERMITIDO_ID = 1378977225776304169


# --- Evento: Cuando el Bot Está Listo ---
@bot.event
async def on_ready():
    """Se ejecuta cuando el bot se conecta a Discord."""
    print(f"✅ Bot conectado como {bot.user}")

    # Intenta enviar el mensaje de reglas al inicio.
    await enviar_reglas()

    # Sincroniza los comandos de barra diagonal (slash commands) con Discord.
    # Es crucial para que los comandos como '/anuncio' aparezcan y funcionen.
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} comandos sincronizados")
    except Exception as e:
        print(f"❌ Error sincronizando comandos: {e}")

# --- Función Auxiliar: Enviar Mensaje de Reglas con Botón ---
async def enviar_reglas():
    """Envía el mensaje de reglas con un botón al canal de reglas."""
    canal = bot.get_channel(CANAL_REGLAS_ID)
    if canal is None:
        print("❌ Canal de reglas no encontrado. Verifica CANAL_REGLAS_ID.")
        return

    # Comprueba si el mensaje de reglas ya existe para evitar duplicados.
    async for mensaje in canal.history(limit=10): # Busca en los últimos 10 mensajes
        # Asegúrate de que el embed existe y tiene un título antes de intentar acceder a él
        if mensaje.author == bot.user and mensaje.embeds and "Bienvenidos al servidor oficial" in mensaje.embeds[0].title:
            print("ℹ️ Mensaje de reglas ya existe. No se enviará de nuevo.")
            return

    # Crea el Embed (mensaje visual) de las reglas
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

    # Crea la vista con el botón
    view = BotonRolView()
    # Envía el mensaje con el embed y el botón
    await canal.send(embed=embed, view=view)

# --- Clase para el Botón de Aceptar Reglas ---
class BotonRolView(discord.ui.View):
    """Representa la vista que contiene el botón para aceptar las reglas."""
    def __init__(self):
        # El 'timeout=None' hace que el botón permanezca activo indefinidamente.
        super().__init__(timeout=None)

    @discord.ui.button(label="¡Aceptar Reglas y Unirme!", style=discord.ButtonStyle.success, custom_id="aceptar_reglas")
    async def aceptar(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Callback que se ejecuta cuando el botón 'Aceptar Reglas' es presionado."""
        # Obtiene el objeto del rol en el servidor.
        rol = interaction.guild.get_role(ROL_ID)

        # Verifica si el usuario ya tiene el rol.
        if rol in interaction.user.roles:
            await interaction.response.send_message("¡Ya tienes el rol, dibujito!", ephemeral=True)
        else:
            # Asigna el rol al usuario.
            await interaction.user.add_roles(rol)
            await interaction.response.send_message("🎉 ¡Rol asignado! Bienvenido a la pandilla 🎨", ephemeral=True)

# --- Comando de Barra Diagonal (Slash Command): /anuncio ---
# Este comando permite enviar anuncios. Su comportamiento depende del canal de uso.
@bot.tree.command(name="anuncio", description="Envía un anuncio con formato especial o general.")
@app_commands.describe(mensaje="El contenido del anuncio.")
@app_commands.has_role(ROL_ANUNCIO_PERMITIDO_ID) # ¡NUEVO! Solo este rol puede usar /anuncio
async def anuncio(interaction: discord.Interaction, mensaje: str):
    """
    Comando para enviar un anuncio.
    - Si se usa en CANAL_ANUNCIOS_GENERAL_ID o CANAL_ANUNCIOS_ROBUX_ID, envía un embed completo.
    - Si se usa en CANALES_TEXTO_PLANO_BOLD_IDS, envía el mensaje en negrita al canal actual.
    Uso: /anuncio <tu_mensaje>
    """
    try:
        # Canal desde donde se ejecutó el comando
        canal_de_ejecucion_id = interaction.channel_id

        # Definir el canal de destino
        canal_destino = None

        # --- Lógica para determinar el canal de destino y el formato ---
        if canal_de_ejecucion_id == CANAL_ANUNCIOS_GENERAL_ID:
            canal_destino = bot.get_channel(CANAL_ANUNCIOS_GENERAL_ID)
            formato_especial = False # Usar embed completo
        elif canal_de_ejecucion_id == CANAL_ANUNCIOS_ROBUX_ID:
            canal_destino = bot.get_channel(CANAL_ANUNCIOS_ROBUX_ID)
            formato_especial = False # Usar embed completo
        elif canal_de_ejecucion_id in CANALES_TEXTO_PLANO_BOLD_IDS:
            canal_destino = bot.get_channel(canal_de_ejecucion_id) # El canal de destino es el mismo
            formato_especial = True # Usar texto en negrita sin embed
        else:
            # Si el comando se usa en un canal no especificado, por defecto se envía al canal general de anuncios
            canal_destino = bot.get_channel(CANAL_ANUNCIOS_GENERAL_ID)
            formato_especial = False

        # --- Verificación del canal de destino ---
        if canal_destino is None:
            await interaction.response.send_message("❌ No se encontró el canal de destino para el anuncio. Verifica los IDs de los canales.", ephemeral=True)
            return

        # --- Envío del mensaje según el formato ---
        if formato_especial:
            # Enviar solo el mensaje en negrita al canal donde se usó el comando
            await canal_destino.send(f"**{mensaje}**")
        else:
            # Enviar un embed completo al canal de anuncios general o de robux
            embed = discord.Embed(
                title="📢 Anuncio Oficial",
                description=mensaje,
                color=discord.Color.blue()
            )
            # embed.set_footer(text=f"Publicado por {interaction.user.display_name}") # Comentado como solicitaste
            await canal_destino.send(embed=embed)

        # Confirmación al usuario
        await interaction.response.send_message(f"✅ ¡Anuncio enviado con éxito a {canal_destino.mention}!", ephemeral=True)

    except Exception as e:
        print(f"❌ Error en el comando /anuncio: {e}")
        await interaction.response.send_message("❌ Hubo un error al intentar enviar el anuncio. Consulta la consola del bot.", ephemeral=True)

# --- Manejo de errores para comandos de barra diagonal (Slash Commands) ---
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingRole):
        # Envía un mensaje si el usuario no tiene el rol necesario
        await interaction.response.send_message(f"❌ ¡Lo siento, {interaction.user.mention}! No tienes el rol necesario para usar este comando.", ephemeral=True)
    else:
        # Para otros errores, envía un mensaje genérico y loguéalos para depuración
        print(f"❌ Error en un comando de barra diagonal: {error}")
        await interaction.response.send_message("❌ Hubo un error al ejecutar este comando. Inténtalo de nuevo más tarde.", ephemeral=True)


# --- Ejecución del Bot (¡MODIFICADO PARA USAR EL TOKEN SEGURO!) ---
keep_alive() # ¡Añade esta línea aquí!
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
