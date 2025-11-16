import discord
from discord.ext import commands, tasks
import json
import random
import asyncio
import os
from datetime import datetime, timedelta

# --- KONFIGURACIJA ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- KLASE ---
class Vilenjak:
    def __init__(self, user_id):
        self.user_id = user_id
        self.ime = f"Vilenjak_{random.randint(1000,9999)}"
        self.nivo = 1
        self.iskustvo = 0
        self.snowflakes = 100
        self.radionica = "Prazna"
        self.kucica = "Osnovna"
        self.vjestine = {
            "pravi_igracke": 1,
            "pakira_poklone": 1,
            "briga_o_jelenima": 1,
            "carolija": 1
        }
        self.inventory = {
            "lampice": [],
            "kugle": [],
            "vrh_jelke": [],
            "ostali_ukrasi": []
        }
        self.jelka_level = 0
        self.jelka_xp = 0
        self.zadnji_zadatak = None
        self.login_streak = 0

# --- POBOLJŠANI SHOP ---
vilenjacki_shop = {
    "lampice": {
        "obicne_lampice": {"cijena": 50, "bonus": "+1 sjaj jelke", "boja": "⚪"},
        "zute_lampice": {"cijena": 80, "bonus": "+2 sjaj jelke", "boja": "🟡"},
        "crvene_lampice": {"cijena": 100, "bonus": "+3 sjaj jelke", "boja": "🔴"},
        "plave_lampice": {"cijena": 120, "bonus": "+4 sjaj jelke", "boja": "🔵"},
        "dugine_lampice": {"cijena": 200, "bonus": "+5 sjaj jelke", "boja": "🌈"},
        "magicne_lampice": {"cijena": 300, "bonus": "+10 sjaj jelke", "boja": "✨"}
    },
    "kugle": {
        "crvena_kugla": {"cijena": 40, "bonus": "+1 ljepota jelke", "boja": "🔴"},
        "zlatna_kugla": {"cijena": 60, "bonus": "+2 ljepota jelke", "boja": "🟡"},
        "plava_kugla": {"cijena": 70, "bonus": "+3 ljepota jelke", "boja": "🔵"},
        "zelen_kugla": {"cijena": 80, "bonus": "+4 ljepota jelke", "boja": "🟢"},
        "srebrna_kugla": {"cijena": 100, "bonus": "+5 ljepota jelke", "boja": "⚪"},
        "kristalna_kugla": {"cijena": 150, "bonus": "+8 ljepota jelke", "boja": "💎"}
    },
    "vrhovi": {
        "obicna_zvijezda": {"cijena": 100, "bonus": "+5 ukupni bonus", "boja": "⭐"},
        "srebrna_zvijezda": {"cijena": 200, "bonus": "+10 ukupni bonus", "boja": "🌟"},
        "zlatna_zvijezda": {"cijena": 300, "bonus": "+15 ukupni bonus", "boja": "💫"},
        "andjeo": {"cijena": 250, "bonus": "+12 ukupni bonus", "boja": "👼"},
        "snjezna_vila": {"cijena": 400, "bonus": "+20 ukupni bonus", "boja": "❄️"}
    },
    "ostali_ukrasi": {
        "snic": {"cijena": 30, "bonus": "+1 srecu", "boja": "❄️"},
        "cokoladica": {"cijena": 25, "bonus": "+1 slatkoca", "boja": "🍫"},
        "cokoladicni_djed": {"cijena": 50, "bonus": "+2 slatkoca", "boja": "🎅"},
        "zvezda": {"cijena": 35, "bonus": "+1 sjaj", "boja": "⭐"},
        "srce": {"cijena": 45, "bonus": "+1 ljubav", "boja": "❤️"},
        "zvono": {"cijena": 55, "bonus": "+1 zvuk", "boja": "🔔"}
    }
}

# --- ZADACI SA 8H COOLDOWN ---
dnevni_zadaci = {
    "pravi_igracke": {
        "opis": "Napravi 10 drvenih igracka za dobru djecu",
        "iskustvo": 50,
        "snowflakes": 25,
        "potrebna_vjestina": "pravi_igracke",
        "cooldown": 8  # sati
    },
    "pakiraj_poklone": {
        "opis": "Zamotaj 15 poklona za posebno dobru djecu",
        "iskustvo": 40,
        "snowflakes": 20,
        "potrebna_vjestina": "pakira_poklone",
        "cooldown": 8
    },
    "njega_jelena": {
        "opis": "Cetkaj i hrani Rudolpha i ostale jelene",
        "iskustvo": 35,
        "snowflakes": 30,
        "potrebna_vjestina": "briga_o_jelenima",
        "cooldown": 8
    },
    "carolija_snijega": {
        "opis": "Baci caroliju za bijeli Bozic",
        "iskustvo": 60,
        "snowflakes": 40,
        "potrebna_vjestina": "carolija",
        "cooldown": 8
    },
    "ciscenje_radionice": {
        "opis": "Ocisti radionicu za nove projekte",
        "iskustvo": 30,
        "snowflakes": 15,
        "potrebna_vjestina": "pravi_igracke",
        "cooldown": 8
    }
}

# --- GLOBALNE VARIJABLE ---
vilenjaci = {}
aktivni_zadaci = {}
cooldown_zadaci = {}

# --- FUNKCIJE ZA SPREMANJE ---
def load_vilenjaci():
    global vilenjaci
    try:
        if os.path.exists('vilenjaci.json'):
            with open('vilenjaci.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                for user_id, vilenjak_data in data.items():
                    vilenjak = Vilenjak(user_id)
                    for key, value in vilenjak_data.items():
                        setattr(vilenjak, key, value)
                    vilenjaci[user_id] = vilenjak
            print(f"📂 Učitano {len(vilenjaci)} vilenjaka")
    except Exception as e:
        print(f"❌ Greška pri učitavanju: {e}")
        vilenjaci = {}

def save_vilenjaci():
    try:
        data = {}
        for user_id, vilenjak in vilenjaci.items():
            data[user_id] = vilenjak.__dict__

        with open('vilenjaci.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Greška pri spremanju: {e}")

# --- POMOĆNE FUNKCIJE ---
def can_do_zadatak(user_id, zadatak_id):
    """Provjeri može li korisnik raditi zadatak (cooldown)"""
    if user_id not in cooldown_zadaci:
        return True

    if zadatak_id not in cooldown_zadaci[user_id]:
        return True

    zadnji_put = cooldown_zadaci[user_id][zadatak_id]
    cooldown_sati = dnevni_zadaci[zadatak_id]['cooldown']
    vrijeme_proslo = datetime.now() - zadnji_put

    return vrijeme_proslo.total_seconds() >= cooldown_sati * 3600

def get_cooldown_remaining(user_id, zadatak_id):
    """Vrati preostalo vrijeme cooldowna"""
    if user_id not in cooldown_zadaci or zadatak_id not in cooldown_zadaci[user_id]:
        return 0

    zadnji_put = cooldown_zadaci[user_id][zadatak_id]
    cooldown_sati = dnevni_zadaci[zadatak_id]['cooldown']
    vrijeme_proslo = datetime.now() - zadnji_put
    preostalo = (cooldown_sati * 3600) - vrijeme_proslo.total_seconds()

    return max(0, preostalo)

def format_time(seconds):
    """Formatiraj vrijeme u čitljiv oblik"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}h {minutes}m"

def calculate_jelka_stats(vilenjak):
    """Izračunaj ukupne statove jelke"""
    ukupni_sjaj = 0
    ukupna_ljepota = 0
    ukupni_bonus = 0

    # Lampice
    for lampica in vilenjak.inventory["lampice"]:
        if lampica in vilenjacki_shop["lampice"]:
            bonus_str = vilenjacki_shop["lampice"][lampica]["bonus"]
            ukupni_sjaj += int(bonus_str.split("+")[1].split(" ")[0])

    # Kugle
    for kugla in vilenjak.inventory["kugle"]:
        if kugla in vilenjacki_shop["kugle"]:
            bonus_str = vilenjacki_shop["kugle"][kugla]["bonus"]
            ukupna_ljepota += int(bonus_str.split("+")[1].split(" ")[0])

    # Vrh
    for vrh in vilenjak.inventory["vrh_jelke"]:
        if vrh in vilenjacki_shop["vrhovi"]:
            bonus_str = vilenjacki_shop["vrhovi"][vrh]["bonus"]
            ukupni_bonus += int(bonus_str.split("+")[1].split(" ")[0])

    return ukupni_sjaj, ukupna_ljepota, ukupni_bonus

# --- KOMANDE ---
@bot.command()
async def postani_vilenjak(ctx):
    """Počni svoju vilenjačku avanturu!"""
    user_id = str(ctx.author.id)

    if user_id in vilenjaci:
        await ctx.send("🎅 Već si vilenjak! Koristi `!mojstatus` za pregled.")
        return

    novi_vilenjak = Vilenjak(user_id)
    vilenjaci[user_id] = novi_vilenjak
    save_vilenjaci()

    embed = discord.Embed(
        title=f"🎄 Dobrodošao/la, {novi_vilenjak.ime}!",
        description="Dobrodošao/la u Selo Djeda Mraz! 🎅",
        color=discord.Color.green()
    )
    embed.add_field(name="🎁 Početni snowflakes", value="100 ❄️", inline=True)
    embed.add_field(name="🏠 Tvoja kućica", value="Osnovna vilenjačka kućica", inline=True)
    embed.add_field(name="🛠️ Radionica", value="Prazna - kupi ukrase u shopu!", inline=True)
    embed.add_field(name="🌲 Tvoja jelka", value="Level 0 - kupi ukrase da je ukrasiš!", inline=True)
    embed.add_field(name="📋 Prvi zadatak", value="Koristi `!zadaci` za prvi posao!", inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def mojstatus(ctx):
    """Prikaži svoj vilenjački status"""
    user_id = str(ctx.author.id)
    vilenjak = vilenjaci.get(user_id)

    if not vilenjak:
        await ctx.send("🎅 Nisi vilenjak! Koristi `!postani_vilenjak` da počneš.")
        return

    sjaj, ljepota, bonus = calculate_jelka_stats(vilenjak)

    embed = discord.Embed(
        title=f"🎄 Status: {vilenjak.ime}",
        color=discord.Color.blue()
    )
    embed.add_field(name="📊 Nivo", value=f"Level {vilenjak.nivo}", inline=True)
    embed.add_field(name="⭐ XP", value=f"{vilenjak.iskustvo}/100", inline=True)
    embed.add_field(name="❄️ Snowflakes", value=f"{vilenjak.snowflakes} ❄️", inline=True)
    embed.add_field(name="🏠 Kućica", value=vilenjak.kucica, inline=True)
    embed.add_field(name="🛠️ Radionica", value=vilenjak.radionica, inline=True)
    embed.add_field(name="🌲 Jelka Level", value=f"Level {vilenjak.jelka_level}", inline=True)

    # Vještine
    vjestine_text = "\n".join([f"{k}: Lvl {v}" for k, v in vilenjak.vjestine.items()])
    embed.add_field(name="🎯 Vještine", value=vjestine_text, inline=False)

    # Stats jelke
    embed.add_field(name="✨ Stats Jelke", 
                   value=f"Sjaj: +{sjaj} | Ljepota: +{ljepota} | Bonus: +{bonus}", 
                   inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def shop(ctx, kategorija: str = None):
    """Prikaži vilenjački shop s ukrasima"""
    if not kategorija:
        embed = discord.Embed(
            title="🏪 VILENJAČKI SHOP - Kategorije Ukrasa",
            color=discord.Color.gold()
        )
        embed.add_field(name="💡 Lampice", value="`!shop lampice` - Razne boje lampica", inline=True)
        embed.add_field(name="🎄 Kugle", value="`!shop kugle` - Božićne kugle", inline=True)
        embed.add_field(name="⭐ Vrhovi", value="`!shop vrhovi` - Vrhovi za jelku", inline=True)
        embed.add_field(name="🎁 Ostali Ukrasi", value="`!shop ostali_ukrasi` - Razni ukrasi", inline=True)
        await ctx.send(embed=embed)
        return

    if kategorija not in vilenjacki_shop:
        await ctx.send("❌ Dostupne kategorije: `lampice`, `kugle`, `vrhovi`, `ostali_ukrasi`")
        return

    embed = discord.Embed(
        title=f"🏪 SHOP - {kategorija.replace('_', ' ').title()}",
        color=discord.Color.gold()
    )

    for item, details in vilenjacki_shop[kategorija].items():
        embed.add_field(
            name=f"{details['boja']} {item.replace('_', ' ').title()}",
            value=f"Cijena: {details['cijena']} ❄️\nBonus: {details['bonus']}",
            inline=True
        )

    embed.set_footer(text="Koristi `!kupi [item]` za kupovinu!")
    await ctx.send(embed=embed)

@bot.command()
async def kupi(ctx, *, item_ime: str):
    """Kupi ukras za svoju jelku"""
    user_id = str(ctx.author.id)
    vilenjak = vilenjaci.get(user_id)

    if not vilenjak:
        await ctx.send("🎅 Nisi vilenjak!")
        return

    item_pronaden = None
    kategorija_pronadena = None

    for kategorija, items in vilenjacki_shop.items():
        for item, details in items.items():
            if item.lower() == item_ime.lower().replace(" ", "_"):
                item_pronaden = details
                kategorija_pronadena = kategorija
                break

    if not item_pronaden:
        await ctx.send("❌ Ukras nije pronađen u shopu!")
        return

    if vilenjak.snowflakes < item_pronaden['cijena']:
        await ctx.send(f"❌ Nemaš dovoljno snowflakes! Trebaš {item_pronaden['cijena']} ❄️, a imaš {vilenjak.snowflakes} ❄️")
        return

    vilenjak.snowflakes -= item_pronaden['cijena']

    # Dodaj u odgovarajuću kategoriju inventorya
    if kategorija_pronadena == "lampice":
        vilenjak.inventory["lampice"].append(item_ime)
    elif kategorija_pronadena == "kugle":
        vilenjak.inventory["kugle"].append(item_ime)
    elif kategorija_pronadena == "vrhovi":
        vilenjak.inventory["vrh_jelke"].append(item_ime)
    elif kategorija_pronadena == "ostali_ukrasi":
        vilenjak.inventory["ostali_ukrasi"].append(item_ime)

    # Dodaj XP jelki
    vilenjak.jelka_xp += 10
    if vilenjak.jelka_xp >= 100:
        vilenjak.jelka_level += 1
        vilenjak.jelka_xp = 0

    save_vilenjaci()

    await ctx.send(f"🎉 Kupio/la si **{item_ime.replace('_', ' ').title()}** {item_pronaden['boja']}!\n"
                  f"💰 Preostalo snowflakes: {vilenjak.snowflakes} ❄️\n"
                  f"🌲 Jelka XP: +10 (Ukupno: {vilenjak.jelka_xp}/100)")

@bot.command()
async def zadaci(ctx):
    """Prikaži dostupne zadatke sa cooldownom"""
    user_id = str(ctx.author.id)
    vilenjak = vilenjaci.get(user_id)

    if not vilenjak:
        await ctx.send("🎅 Nisi vilenjak!")
        return

    embed = discord.Embed(
        title="📋 DOSTUPNI ZADACI (8h cooldown)",
        color=discord.Color.blue()
    )

    for zadatak_id, zadatak in dnevni_zadaci.items():
        dostupan = can_do_zadatak(user_id, zadatak_id)
        cooldown_text = ""

        if not dostupan:
            preostalo = get_cooldown_remaining(user_id, zadatak_id)
            cooldown_text = f"⏰ Cooldown: {format_time(preostalo)}"

        status = "✅ Dostupan" if dostupan else "❌ Na cooldownu"

        embed.add_field(
            name=f"🎯 {zadatak_id.replace('_', ' ').title()} - {status}",
            value=f"{zadatak['opis']}\n"
                  f"Nagrada: {zadatak['snowflakes']} ❄️ + {zadatak['iskustvo']} XP\n"
                  f"{cooldown_text}\n"
                  f"Koristi: `!radi {zadatak_id}`",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command()
async def radi(ctx, zadatak_id: str):
    """Započni rad na zadatku"""
    user_id = str(ctx.author.id)

    if user_id in aktivni_zadaci:
        await ctx.send("❌ Već radiš na zadatku! Pričekaj da završiš trenutni.")
        return

    vilenjak = vilenjaci.get(user_id)
    if not vilenjak:
        await ctx.send("🎅 Nisi vilenjak!")
        return

    if zadatak_id not in dnevni_zadaci:
        await ctx.send("❌ Zadataka nije pronađen!")
        return

    # Provjeri cooldown
    if not can_do_zadatak(user_id, zadatak_id):
        preostalo = get_cooldown_remaining(user_id, zadatak_id)
        await ctx.send(f"❌ Ovaj zadatak je na cooldownu! Pričekaj još {format_time(preostalo)}")
        return

    zadatak = dnevni_zadaci[zadatak_id]
    potrebna_vjestina = zadatak['potrebna_vjestina']

    if potrebna_vjestina not in vilenjak.vjestine or vilenjak.vjestine[potrebna_vjestina] < 1:
        await ctx.send("❌ Nemaš dovoljno vještine za ovaj zadatak!")
        return

    # Započni zadatak
    aktivni_zadaci[user_id] = zadatak_id

    await ctx.send(f"🔨 **Započinješ zadatak:** {zadatak_id.replace('_', ' ').title()}\n"
                  f"📝 {zadatak['opis']}\n"
                  f"⏰ Zadatak traje 30 sekundi...")

    # Simuliraj rad (30 sekundi umjesto 8 sati za testiranje)
    await asyncio.sleep(30)

    # Završi zadatak
    if user_id in aktivni_zadaci and aktivni_zadaci[user_id] == zadatak_id:
        # Dodaj nagrade
        vilenjak.snowflakes += zadatak['snowflakes']
        vilenjak.iskustvo += zadatak['iskustvo']

        # Postavi cooldown
        if user_id not in cooldown_zadaci:
            cooldown_zadaci[user_id] = {}
        cooldown_zadaci[user_id][zadatak_id] = datetime.now()

        # Level up provjera
        if vilenjak.iskustvo >= 100:
            vilenjak.nivo += 1
            vilenjak.iskustvo = 0
            await ctx.send(f"🎉 **LEVEL UP!** Sada si Level {vilenjak.nivo}!")

        # Povećaj vještinu (šansa)
        if random.random() < 0.3:
            vilenjak.vjestine[potrebna_vjestina] += 1
            await ctx.send(f"🌟 **Vještina poboljšana!** {potrebna_vjestina} sada Level {vilenjak.vjestine[potrebna_vjestina]}")

        # Ukloni iz aktivnih zadataka
        del aktivni_zadaci[user_id]
        save_vilenjaci()

        await ctx.send(f"✅ **Završio/la si zadatak!**\n"
                      f"💰 Zaradio/la: {zadatak['snowflakes']} ❄️\n"
                      f"⭐ Dobio/la: {zadatak['iskustvo']} XP\n"
                      f"💰 Ukupno snowflakes: {vilenjak.snowflakes} ❄️\n"
                      f"⏰ Sljedeći put možeš raditi ovaj zadatak za 8 sati")
    else:
        await ctx.send("❌ Zadatak je prekinut!")

@bot.command()
async def inventory(ctx, member: discord.Member = None):
    """Prikaži svoje ili tuđe ukrase"""
    target_member = member or ctx.author
    user_id = str(target_member.id)
    vilenjak = vilenjaci.get(user_id)

    if not vilenjak:
        if member:
            await ctx.send(f"🎅 {member.display_name} nije vilenjak!")
        else:
            await ctx.send("🎅 Nisi vilenjak! Koristi `!postani_vilenjak` da počneš.")
        return

    sjaj, ljepota, bonus = calculate_jelka_stats(vilenjak)

    embed = discord.Embed(
        title=f"🎒 INVENTORY - {target_member.display_name}",
        description=f"🌲 Jelka Level: {vilenjak.jelka_level} | XP: {vilenjak.jelka_xp}/100\n"
                   f"✨ Stats: Sjaj +{sjaj} | Ljepota +{ljepota} | Bonus +{bonus}",
        color=discord.Color.purple()
    )

    for kategorija, items in vilenjak.inventory.items():
        if items:
            # Grupiraj iste iteme
            item_count = {}
            for item in items:
                item_count[item] = item_count.get(item, 0) + 1

            items_text = []
            for item, count in item_count.items():
                if item in vilenjacki_shop.get(kategorija, {}):
                    boja = vilenjacki_shop[kategorija][item]["boja"]
                    items_text.append(f"{boja} {item.replace('_', ' ').title()} x{count}")
                else:
                    items_text.append(f"{item.replace('_', ' ').title()} x{count}")

            embed.add_field(
                name=f"📦 {kategorija.replace('_', ' ').title()}",
                value="\n".join(items_text) if items_text else "Prazno",
                inline=True
            )
        else:
            embed.add_field(
                name=f"📦 {kategorija.replace('_', ' ').title()}",
                value="Prazno",
                inline=True
            )

    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def reset(ctx, member: discord.Member):
    """Resetiraj vilenjaka (samo admini)"""
    user_id = str(member.id)

    if user_id not in vilenjaci:
        await ctx.send(f"❌ {member.display_name} nije vilenjak!")
        return

    # Obriši vilenjaka
    del vilenjaci[user_id]

    # Obriši iz cooldowna
    if user_id in cooldown_zadaci:
        del cooldown_zadaci[user_id]

    # Obriši iz aktivnih zadataka
    if user_id in aktivni_zadaci:
        del aktivni_zadaci[user_id]

    save_vilenjaci()

    await ctx.send(f"✅ **{member.display_name} je resetiran!**\n"
                  f"🎅 Sada mora ponovo koristiti `!postani_vilenjak` da počne ispočetka.")

@reset.error
async def reset_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Samo administratori mogu koristiti ovu komandu!")

@bot.command()
async def jelka(ctx, member: discord.Member = None):
    """Prikaži jelku s ukrasima"""
    target_member = member or ctx.author
    user_id = str(target_member.id)
    vilenjak = vilenjaci.get(user_id)

    if not vilenjak:
        if member:
            await ctx.send(f"🎅 {member.display_name} nema jelku!")
        else:
            await ctx.send("🎅 Nemaš jelku! Postani vilenjak sa `!postani_vilenjak`")
        return

    sjaj, ljepota, bonus = calculate_jelka_stats(vilenjak)

    # Kreiraj vizualnu jelku
    jelka_visual = []
    jelka_visual.append(" " * 4 + "🌲" * 3)
    jelka_visual.append(" " * 3 + "🌲" * 5) 
    jelka_visual.append(" " * 2 + "🌲" * 7)
    jelka_visual.append(" " * 1 + "🌲" * 9)
    jelka_visual.append("🌲" * 11)
    jelka_visual.append(" " * 4 + "🎁" * 3)

    # Dodaj ukrase na jelku
    ukrasi_text = []
    for kategorija, items in vilenjak.inventory.items():
        for item in items[:3]:  # Prikaži samo prva 3 iz svake kategorije
            if item in vilenjacki_shop.get(kategorija, {}):
                boja = vilenjacki_shop[kategorija][item]["boja"]
                ukrasi_text.append(boja)

    embed = discord.Embed(
        title=f"🎄 Jelka - {target_member.display_name}",
        description=f"```\n" + "\n".join(jelka_visual) + "\n```",
        color=discord.Color.green()
    )

    embed.add_field(name="📊 Level Jelke", value=f"Level {vilenjak.jelka_level}", inline=True)
    embed.add_field(name="⭐ XP Jelke", value=f"{vilenjak.jelka_xp}/100", inline=True)
    embed.add_field(name="✨ Ukrasi", value=" ".join(ukrasi_text[:10]), inline=True)
    embed.add_field(name="📈 Stats", 
                   value=f"**Sjaj:** +{sjaj}\n**Ljepota:** +{ljepota}\n**Bonus:** +{bonus}", 
                   inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def leaderboard(ctx):
    """Prikaži najbolje vilenjake"""
    if not vilenjaci:
        await ctx.send("🎅 Još nema vilenjaka! Budi prvi koji će koristiti `!postani_vilenjak`")
        return

    sortirani_vilenjaci = sorted(
        vilenjaci.values(), 
        key=lambda x: (x.jelka_level, x.nivo, x.snowflakes), 
        reverse=True
    )[:10]

    embed = discord.Embed(
        title="🏆 VILENJAČKI LEADERBOARD - TOP 10",
        description="Rangirani po levelu jelke",
        color=discord.Color.gold()
    )

    for i, vilenjak in enumerate(sortirani_vilenjaci, 1):
        member = ctx.guild.get_member(int(vilenjak.user_id))
        ime = member.display_name if member else vilenjak.ime

        embed.add_field(
            name=f"{i}. {ime}",
            value=f"🌲 Level {vilenjak.jelka_level} | 👤 Level {vilenjak.nivo} | ❄️ {vilenjak.snowflakes}",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command()
async def pomoc(ctx):
    """Prikaži sve dostupne komande"""
    embed = discord.Embed(
        title="🎅 VILENJAČKE KOMANDE - POMOĆ",
        color=discord.Color.blue()
    )

    komande = [
        ("`!postani_vilenjak`", "Započni vilenjačku avanturu"),
        ("`!mojstatus`", "Vidi svoj status i vještine"),
        ("`!shop [kategorija]`", "Otvori shop s ukrasima"),
        ("`!kupi [ukras]`", "Kupi ukras za jelku"),
        ("`!zadaci`", "Vidi zadatke (8h cooldown)"),
        ("`!radi [zadatak]`", "Započni rad na zadatku"),
        ("`!inventory [@user]`", "Vidi svoje/tuđe ukrase"),
        ("`!jelka [@user]`", "Prikaži jelku s ukrasima"),
        ("`!leaderboard`", "Vidi najbolje vilenjake"),
        ("`!reset @user`", "**ADMIN** - Resetiraj vilenjaka"),
        ("`!pomoc`", "Ova poruka pomoći")
    ]

    for komanda, opis in komande:
        embed.add_field(name=komanda, value=opis, inline=False)

    await ctx.send(embed=embed)

# --- BOT EVENTI ---
@bot.event
async def on_ready():
    print(f"🎅 {bot.user} je online i spreman za vilenjačku avanturu!")
    load_vilenjaci()

# --- POKRETANJE BOTA ---
if __name__ == "__main__":
    load_vilenjaci()
    token = os.environ.get('DISCORD_TOKEN')
    
    if not token:
        print("❌ DISCORD_TOKEN nije postavljen!")
        print("🔍 Provjeri Railway Variables")
        exit(1)
    
    try:
        bot.run(token)
    except Exception as e:
        print(f"❌ Greška pri pokretanju: {e}")
        exit(1)
