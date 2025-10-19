import discord
from discord.ext import tasks, commands
import json
import random
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class Vilenjak:
    def __init__(self, user_id):
        self.user_id = user_id
        self.ime = f"Vilenjak#{user_id[:4]}"
        self.nivo = 1
        self.iskustvo = 0
        self.snowflakes = 100
        self.kućica = "Osnovna vilenjačka kućica"
        self.radionica = "Osnovna radionica"
        self.vještine = {
            "izrada_igračaka": 1,
            "ukrašavanje": 1,
            "pakiranje": 1,
            "pečenje": 1
        }
        self.inventory = {
            "dekoracije": [],
            "alat": []
        }
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "ime": self.ime,
            "nivo": self.nivo,
            "iskustvo": self.iskustvo,
            "snowflakes": self.snowflakes,
            "kućica": self.kućica,
            "radionica": self.radionica,
            "vještine": self.vještine,
            "inventory": self.inventory
        }
    
    @staticmethod
    def from_dict(data):
        vilenjak = Vilenjak(data["user_id"])
        vilenjak.ime = data.get("ime", vilenjak.ime)
        vilenjak.nivo = data.get("nivo", 1)
        vilenjak.iskustvo = data.get("iskustvo", 0)
        vilenjak.snowflakes = data.get("snowflakes", 100)
        vilenjak.kućica = data.get("kućica", "Osnovna vilenjačka kućica")
        vilenjak.radionica = data.get("radionica", "Osnovna radionica")
        vilenjak.vještine = data.get("vještine", vilenjak.vještine)
        vilenjak.inventory = data.get("inventory", vilenjak.inventory)
        return vilenjak

vilenjacki_shop = {
    "alat": {
        "čekić_od_zlata": {"cijena": 200, "bonus": "+20% brzina izrade"},
        "magični_nož": {"cijena": 150, "bonus": "+15% kvaliteta"},
        "božićna_pila": {"cijena": 180, "bonus": "+10% efikasnost"}
    },
    "dekoracije": {
        "božićno_drvce": {"cijena": 50, "bonus": "+5% snowflakes"},
        "lampice": {"cijena": 75, "bonus": "+3 sreća"},
        "vjenčić": {"cijena": 60, "bonus": "+2 XP po zadatku"}
    },
    "nadogradnje": {
        "veća_radionica": {"cijena": 500, "bonus": "+2 zadatka istovremeno"},
        "čarobna_peć": {"cijena": 750, "bonus": "2x iskustvo"}
    }
}

dnevni_zadaci = {
    "izradi_igračku": {
        "opis": "Izradi božićnu igračku za djecu",
        "snowflakes": 50,
        "iskustvo": 20,
        "vrijeme": 10,
        "potrebna_vještina": "izrada_igračaka"
    },
    "ukrasi_kuglicu": {
        "opis": "Ukrasi božićne kuglice",
        "snowflakes": 40,
        "iskustvo": 15,
        "vrijeme": 8,
        "potrebna_vještina": "ukrašavanje"
    },
    "zapakuj_poklon": {
        "opis": "Zapakuj poklon u božićni papir",
        "snowflakes": 35,
        "iskustvo": 12,
        "vrijeme": 5,
        "potrebna_vještina": "pakiranje"
    },
    "ispeci_kolače": {
        "opis": "Ispeci božićne kolačiće",
        "snowflakes": 60,
        "iskustvo": 25,
        "vrijeme": 15,
        "potrebna_vještina": "pečenje"
    }
}

bot = commands.Bot(command_prefix="!", intents=intents)
vilenjaci_data = {}

def load_vilenjaci():
    global vilenjaci_data
    try:
        with open("vilenjaci.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            vilenjaci_data = {user_id: Vilenjak.from_dict(v_data) for user_id, v_data in data.items()}
    except FileNotFoundError:
        vilenjaci_data = {}

def save_vilenjaci():
    with open("vilenjaci.json", "w", encoding="utf-8") as f:
        data = {user_id: v.to_dict() for user_id, v in vilenjaci_data.items()}
        json.dump(data, f, indent=2, ensure_ascii=False)

@bot.event
async def on_ready():
    load_vilenjaci()
    print(f'🎄 {bot.user} is online!')
    print(f'🎅 Christmas Bot ready!')

@bot.command()
async def postani_vilenjak(ctx):
    """Počni svoju vilenjačku avanturu!"""
    if str(ctx.author.id) in vilenjaci_data:
        await ctx.send("🎅 Već si vilenjak! Koristi `!mojstatus` za pregled.")
        return

    novi_vilenjak = Vilenjak(str(ctx.author.id))
    vilenjaci_data[str(ctx.author.id)] = novi_vilenjak
    save_vilenjaci()

    embed = discord.Embed(
        title=f"🎄 Dobrodošao/la, {novi_vilenjak.ime}!",
        description="Dobrodošao/la u Selo Djeda Mraz! 🎅",
        color=discord.Color.green()
    )
    embed.add_field(name="🎁 Početni snowflakes", value="100 ❄️", inline=True)
    embed.add_field(name="🏠 Tvoja kućica", value="Osnovna vilenjačka kućica", inline=True)
    embed.add_field(name="🛠️ Radionica", value="Prazna - kupi opremu u shopu!", inline=True)
    embed.add_field(name="📋 Prvi zadatak", value="Koristi `!zadaci` za prvi posao!", inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def mojstatus(ctx):
    """Prikaži svoj vilenjački status"""
    vilenjak = vilenjaci_data.get(str(ctx.author.id))
    if not vilenjak:
        await ctx.send("🎅 Nisi vilenjak! Koristi `!postani_vilenjak` da počneš.")
        return

    embed = discord.Embed(
        title=f"🎄 Status: {vilenjak.ime}",
        color=discord.Color.blue()
    )
    embed.add_field(name="📊 Nivo", value=f"Level {vilenjak.nivo}", inline=True)
    embed.add_field(name="⭐ XP", value=f"{vilenjak.iskustvo}/100", inline=True)
    embed.add_field(name="❄️ Snowflakes", value=f"{vilenjak.snowflakes} ❄️", inline=True)
    embed.add_field(name="🏠 Kućica", value=vilenjak.kućica, inline=True)
    embed.add_field(name="🛠️ Radionica", value=vilenjak.radionica, inline=True)

    vještine_text = "\n".join([f"{k}: Lvl {v}" for k, v in vilenjak.vještine.items()])
    embed.add_field(name="🎯 Vještine", value=vještine_text, inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def shop(ctx, kategorija: str = None):
    """Prikaži vilenjački shop"""
    if not kategorija:
        embed = discord.Embed(
            title="🏪 VILENJAČKI SHOP - Kategorije",
            color=discord.Color.gold()
        )
        embed.add_field(name="🛠️ Alat", value="`!shop alat` - Bolji alat za posao", inline=True)
        embed.add_field(name="🎄 Dekoracije", value="`!shop dekoracije` - Ukrasi za kućicu", inline=True)
        embed.add_field(name="🏠 Nadogradnje", value="`!shop nadogradnje` - Poboljšanja", inline=True)
        await ctx.send(embed=embed)
        return

    if kategorija not in vilenjacki_shop:
        await ctx.send("❌ Dostupne kategorije: `alat`, `dekoracije`, `nadogradnje`")
        return

    embed = discord.Embed(
        title=f"🏪 SHOP - {kategorija.title()}",
        color=discord.Color.gold()
    )

    for item, details in vilenjacki_shop[kategorija].items():
        embed.add_field(
            name=f"🎁 {item.replace('_', ' ').title()}",
            value=f"Cijena: {details['cijena']} ❄️\nBonus: {details['bonus']}",
            inline=True
        )

    embed.set_footer(text="Koristi `!kupi [item]` za kupovinu!")
    await ctx.send(embed=embed)

@bot.command()
async def kupi(ctx, *, item_ime: str):
    """Kupi item iz shopa"""
    vilenjak = vilenjaci_data.get(str(ctx.author.id))
    if not vilenjak:
        await ctx.send("🎅 Nisi vilenjak!")
        return

    item_ime_normalized = item_ime.lower().replace(" ", "_")
    
    item_pronaden = None
    kategorija_pronadena = None
    item_key = None

    for kategorija, items in vilenjacki_shop.items():
        for item, details in items.items():
            if item.lower() == item_ime_normalized:
                item_pronaden = details
                kategorija_pronadena = kategorija
                item_key = item
                break

    if not item_pronaden:
        await ctx.send("❌ Item nije pronađen u shopu!")
        return

    if vilenjak.snowflakes < item_pronaden['cijena']:
        await ctx.send(f"❌ Nemaš dovoljno snowflakes! Trebaš {item_pronaden['cijena']} ❄️")
        return

    vilenjak.snowflakes -= item_pronaden['cijena']

    if kategorija_pronadena == "dekoracije":
        vilenjak.inventory["dekoracije"].append(item_ime)
    elif kategorija_pronadena == "alat":
        vilenjak.inventory["alat"].append(item_ime)
    elif kategorija_pronadena == "nadogradnje":
        if item_key == "veća_radionica":
            vilenjak.radionica = "Proširena radionica"
        elif item_key == "čarobna_peć":
            vilenjak.radionica = "Radionica s čarobnom peći"

    save_vilenjaci()

    await ctx.send(f"🎉 Kupio/la si **{item_ime.replace('_', ' ').title()}**!\n"
                  f"💰 Preostalo snowflakes: {vilenjak.snowflakes} ❄️")

@bot.command()
async def zadaci(ctx):
    """Prikaži dostupne zadatke"""
    vilenjak = vilenjaci_data.get(str(ctx.author.id))
    if not vilenjak:
        await ctx.send("🎅 Nisi vilenjak!")
        return

    embed = discord.Embed(
        title="📋 DOSTUPNI ZADACI",
        color=discord.Color.blue()
    )

    for zadatak_id, zadatak in dnevni_zadaci.items():
        embed.add_field(
            name=f"🎯 {zadatak_id.replace('_', ' ').title()}",
            value=f"{zadatak['opis']}\n"
                  f"Nagrada: {zadatak['snowflakes']} ❄️ + {zadatak['iskustvo']} XP\n"
                  f"Vrijeme: {zadatak['vrijeme']} min\n"
                  f"Koristi: `!radi {zadatak_id}`",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command()
async def radi(ctx, zadatak_id: str):
    """Započni rad na zadatku"""
    vilenjak = vilenjaci_data.get(str(ctx.author.id))
    if not vilenjak:
        await ctx.send("🎅 Nisi vilenjak!")
        return

    if zadatak_id not in dnevni_zadaci:
        await ctx.send("❌ Zadataka nije pronađen!")
        return

    zadatak = dnevni_zadaci[zadatak_id]

    if vilenjak.vještine[zadatak['potrebna_vještina']] < 1:
        await ctx.send("❌ Nemaš dovoljno vještine za ovaj zadatak!")
        return

    await ctx.send(f"🔨 Započinješ zadatak: **{zadatak_id.replace('_', ' ').title()}**\n"
                  f"⏰ Trajat će {zadatak['vrijeme']} minuta...")

    await asyncio.sleep(5)

    vilenjak.snowflakes += zadatak['snowflakes']
    vilenjak.iskustvo += zadatak['iskustvo']

    if vilenjak.iskustvo >= 100:
        vilenjak.nivo += 1
        vilenjak.iskustvo = 0
        await ctx.send(f"🎉 **LEVEL UP!** Sada si Level {vilenjak.nivo}!")

    if random.random() < 0.3:
        vilenjak.vještine[zadatak['potrebna_vještina']] += 1
        await ctx.send(f"🌟 **Vještina poboljšana!** {zadatak['potrebna_vještina']} sada Level {vilenjak.vještine[zadatak['potrebna_vještina']]}")

    save_vilenjaci()

    await ctx.send(f"✅ Završio/la si zadatak!\n"
                  f"💰 Zaradio/la: {zadatak['snowflakes']} ❄️\n"
                  f"⭐ Dobio/la: {zadatak['iskustvo']} XP\n"
                  f"💰 Ukupno snowflakes: {vilenjak.snowflakes} ❄️")

@bot.command()
async def leaderboard(ctx):
    """Prikaži najbolje vilenjake"""
    if not vilenjaci_data:
        await ctx.send("🎅 Još nema vilenjaka!")
        return

    sortirani_vilenjaci = sorted(
        vilenjaci_data.values(), 
        key=lambda x: (x.nivo, x.iskustvo), 
        reverse=True
    )[:10]

    embed = discord.Embed(
        title="🏆 VILENJAČKI LEADERBOARD",
        color=discord.Color.gold()
    )

    for i, vilenjak in enumerate(sortirani_vilenjaci, 1):
        member = ctx.guild.get_member(int(vilenjak.user_id))
        ime = member.display_name if member else vilenjak.ime

        embed.add_field(
            name=f"{i}. {ime}",
            value=f"Level {vilenjak.nivo} | {vilenjak.snowflakes} ❄️ | {vilenjak.radionica}",
            inline=False
        )

    await ctx.send(embed=embed)

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    print("❌ DISCORD_BOT_TOKEN nije postavljen!")
    print("Dodaj svoj Discord bot token u Secrets (DISCORD_BOT_TOKEN)")
    exit(1)

bot.run(TOKEN)