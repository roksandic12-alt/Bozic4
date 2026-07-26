import discord
from discord.ext import commands
import json
import random
import os
from datetime import datetime, timedelta

# --- OPTIMIZACIJA INTENATA (LOW RAM FOR RAILWAY) ---
intents = discord.Intents.default()
intents.message_content = True
# Isključeno intents.members jer drastično troši memoriju.

bot = commands.Bot(command_prefix="!", intents=intents)

# --- KLASE ---
class Vilenjak:
    def __init__(self, user_id):
        self.user_id = user_id
        self.ime = f"Vilenjak_{random.randint(1000,9999)}"
        self.nivo = 1
        self.iskustvo = 0
        self.snowflakes = 100
        self.radionica = "Osnovna"
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
        self.jelka_level = 1
        self.jelka_xp = 0

# --- SHOP DEFINICIJA ---
vilenjacki_shop = {
    "lampice": {
        "zute_lampice": {"cijena": 50, "bonus": 2, "boja": "🟡"},
        "crvene_lampice": {"cijena": 60, "bonus": 3, "boja": "🔴"},
        "plave_lampice": {"cijena": 70, "bonus": 4, "boja": "🔵"},
        "magicne_lampice": {"cijena": 120, "bonus": 8, "boja": "✨"}
    },
    "kugle": {
        "crvena_kugla": {"cijena": 30, "bonus": 2, "boja": "🔴"},
        "zlatna_kugla": {"cijena": 45, "bonus": 3, "boja": "🟡"},
        "plava_kugla": {"cijena": 55, "bonus": 4, "boja": "🔵"},
        "kristalna_kugla": {"cijena": 100, "bonus": 7, "boja": "💎"}
    },
    "vrhovi": {
        "obicna_zvijezda": {"cijena": 80, "bonus": 5, "boja": "⭐"},
        "zlatna_zvijezda": {"cijena": 150, "bonus": 12, "boja": "💫"},
        "andjeo": {"cijena": 200, "bonus": 15, "boja": "👼"}
    }
}

dnevni_zadaci = {
    "pravi_igracke": {"opis": "Napravi drvene igračke", "iskustvo": 25, "snowflakes": 40, "vjestina": "pravi_igracke"},
    "pakiraj_poklone": {"opis": "Zamotaj poklone za djecu", "iskustvo": 20, "snowflakes": 35, "vjestina": "pakira_poklone"},
    "njega_jelena": {"opis": "Nahrani Rudolfa i ekipu", "iskustvo": 30, "snowflakes": 50, "vjestina": "briga_o_jelenima"},
    "carolija_snijega": {"opis": "Baci čaroliju za bijeli Božić", "iskustvo": 40, "snowflakes": 60, "vjestina": "carolija"}
}

vilenjaci = {}
cooldown_zadaci = {}

# --- SPREMANJE I UČITAVANJE ---
def load_vilenjaci():
    global vilenjaci
    if os.path.exists('vilenjaci.json'):
        try:
            with open('vilenjaci.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                for user_id, v_data in data.items():
                    v = Vilenjak(user_id)
                    v.__dict__.update(v_data)
                    vilenjaci[user_id] = v
            print(f"📂 Učitano {len(vilenjaci)} vilenjaka.")
        except Exception as e:
            print(f"❌ Greška pri učitavanju JSON-a: {e}")

def save_vilenjaci():
    try:
        data = {user_id: v.__dict__ for user_id, v in vilenjaci.items()}
        with open('vilenjaci.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Greška pri spremanju JSON-a: {e}")

# --- POMOĆNE FUNKCIJE ---
def get_cooldown(user_id, zadatak_id):
    if user_id not in cooldown_zadaci or zadatak_id not in cooldown_zadaci[user_id]:
        return 0
    proslo = datetime.now() - cooldown_zadaci[user_id][zadatak_id]
    preostalo = 28800 - proslo.total_seconds() # 8 sati = 28800 sekundi
    return max(0, preostalo)

def calculate_stats(vilenjak):
    sjaj, ljepota, bonus = 0, 0, 0
    for k in vilenjak.inventory["lampice"]:
        if k in vilenjacki_shop["lampice"]: sjaj += vilenjacki_shop["lampice"][k]["bonus"]
    for k in vilenjak.inventory["kugle"]:
        if k in vilenjacki_shop["kugle"]: ljepota += vilenjacki_shop["kugle"][k]["bonus"]
    for k in vilenjak.inventory["vrh_jelke"]:
        if k in vilenjacki_shop["vrhovi"]: bonus += vilenjacki_shop["vrhovi"][k]["bonus"]
    return sjaj, ljepota, bonus

# --- DINAMIČKO RENDERIRANJE JELKICE ---
def generiraj_jelku_string(vilenjak):
    # Pokupi sve emotikone ukrasa koje igrač ima u inventoryju
    bazen_ukrasa = []
    for k in vilenjak.inventory["lampice"]:
        if k in vilenjacki_shop["lampice"]: bazen_ukrasa.append(vilenjacki_shop["lampice"][k]["boja"])
    for k in vilenjak.inventory["kugle"]:
        if k in vilenjacki_shop["kugle"]: bazen_ukrasa.append(vilenjacki_shop["kugle"][k]["boja"])

    # Odredi vrh jelke
    vrh = "🎄"
    if vilenjak.inventory["vrh_jelke"]:
        zadnji_vrh = vilenjak.inventory["vrh_jelke"][-1]
        if zadnji_vrh in vilenjacki_shop["vrhovi"]:
            vrh = vilenjacki_shop["vrhovi"][zadnji_vrh]["boja"]

    # Šablona grana jelke (broj iglica po redovima)
    redovi_velicine = [1, 3, 5, 7, 9]
    jelka_rows = []
    
    # Postavljanje vrha
    jelka_rows.append(f"   {vrh}   ")

    for max_zelenih in redovi_velicine:
        red_str = ""
        for _ in range(max_zelenih):
            # Ako igrač ima ukrase, postoji 35% šanse da na mjesto iglice stavimo njegov ukras
            if bazen_ukrasa and random.random() < 0.35:
                red_str += random.choice(bazen_ukrasa)
            else:
                red_str += "🌿"
        
        # Centriranje reda radi pravilnog oblika trokuta
        razmak = (9 - max_zelenih) // 1
        jelka_rows.append(" " * razmak + red_str)

    jelka_rows.append("    🟫    ") # Deblo
    jelka_rows.append("  🎁🎁🎁  ") # Pokloni ispod
    
    return "\n".join(jelka_rows)

# --- INTERAKTIVNI GUMBI (ANTI-SPAM UI) ---

class ShopDropdown(discord.ui.Select):
    def __init__(self, vilenjak):
        self.vilenjak = vilenjak
        options = []
        for kat, artikli in vilenjacki_shop.items():
            for art_id, inf in artikli.items():
                options.append(discord.SelectOption(
                    label=f"{art_id.replace('_', ' ').title()}",
                    value=f"{kat}:{art_id}",
                    description=f"Cijena: {inf['cijena']} ❄️ | Bonus: +{inf['bonus']}",
                    emoji=inf['boja']
                ))
        super().__init__(placeholder="Odaberi ukras za kupovinu...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.vilenjak.user_id:
            await interaction.response.send_message("❌ Ovo nije tvoj meni!", ephemeral=True)
            return

        kat, art_id = self.values[0].split(":")
        artikal = vilenjacki_shop[kat][art_id]

        if self.vilenjak.snowflakes < artikal['cijena']:
            await interaction.response.send_message(f"❌ Nemaš dovoljno snowflakesa! Treba ti {artikal['cijena']} ❄️.", ephemeral=True)
            return

        self.vilenjak.snowflakes -= artikal['cijena']
        
        # Razvrstavanje u ispravan inventory ključ
        inv_kljuc = "vrh_jelke" if kat == "vrhovi" else kat
        self.vilenjak.inventory[inv_kljuc].append(art_id)

        # Level up jelke
        self.vilenjak.jelka_xp += 15
        lvl_up_poruka = ""
        if self.vilenjak.jelka_xp >= 100:
            self.vilenjak.jelka_level += 1
            self.vilenjak.jelka_xp = 0
            lvl_up_poruka = f" \n🎄 **Tvoja jelka je narasla na Level {self.vilenjak.jelka_level}!**"

        save_vilenjaci()
        await interaction.response.send_message(f"🎉 Kupio/la si {artikal['boja']} {art_id.replace('_', ' ').title()}! Preostalo: {self.vilenjak.snowflakes} ❄️.{lvl_up_poruka}", ephemeral=True)

class ShopView(discord.ui.View):
    def __init__(self, vilenjak):
        super().__init__(timeout=60)
        self.add_item(ShopDropdown(vilenjak))

class ZadaciView(discord.ui.View):
    def __init__(self, vilenjak):
        super().__init__(timeout=60)
        self.vilenjak = vilenjak
        
        for z_id, z_info in dnevni_zadaci.items():
            self.add_item(discord.ui.Button(label=z_id.replace('_', ' ').title(), style=discord.ui.ButtonStyle.success, custom_id=z_id))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if str(interaction.user.id) != self.vilenjak.user_id:
            await interaction.response.send_message("❌ Ovo nisu tvoji zadaci!", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

    async def dispatch(self, interaction: discord.Interaction):
        z_id = interaction.data['custom_id']
        preostalo = get_cooldown(self.vilenjak.user_id, z_id)
        
        if preostalo > 0:
            sati = int(preostalo // 3600)
            minuti = int((preostalo % 3600) // 60)
            await interaction.response.send_message(f"⏰ Taj zadatak je na cooldownu još {sati}h {minuti}m!", ephemeral=True)
            return

        z_info = dnevni_zadaci[z_id]
        self.vilenjak.snowflakes += z_info['snowflakes']
        self.vilenjak.iskustvo += z_info['iskustvo']

        # Postavi cooldown za 8 sati
        if self.vilenjak.user_id not in cooldown_zadaci:
            cooldown_zadaci[self.vilenjak.user_id] = {}
        cooldown_zadaci[self.vilenjak.user_id][z_id] = datetime.now()

        # Level up vilenjaka
        lvl_tekst = ""
        if self.vilenjak.iskustvo >= 100:
            self.vilenjak.nivo += 1
            self.vilenjak.iskustvo = 0
            lvl_tekst = f"\n🎉 **LEVEL UP! Sada si Level {self.vilenjak.nivo} vilenjak!**"

        save_vilenjaci()
        await interaction.response.send_message(f"✅ **Uspješno obavljeno:** {z_info['opis']}\n Zaradio/la: {z_info['snowflakes']} ❄️ i +{z_info['iskustvo']} XP.{lvl_tekst}", ephemeral=True)

# --- TEKSTUALNE KOMANDE ---

@bot.command()
async def postani_vilenjak(ctx):
    user_id = str(ctx.author.id)
    if user_id in vilenjaci:
        await ctx.send("🎅 Već imaš aktivan vilenjački profil! Unesi `!mojstatus`.")
        return
    vilenjaci[user_id] = Vilenjak(user_id)
    save_vilenjaci()
    await ctx.send(f"🎄 **Dobrodošao/la u radionicu, {vilenjaci[user_id].ime}!** Dobio/la si 100 ❄️. Upiši `!jelka` da vidiš svoj bor.")

@bot.command()
async def mojstatus(ctx):
    user_id = str(ctx.author.id)
    v = vilenjaci.get(user_id)
    if not v:
        await ctx.send("❌ Nisi registriran! Napiši `!postani_vilenjak`.")
        return
    sjaj, ljepota, bonus = calculate_stats(v)
    
    embed = discord.Embed(title=f"📊 Status Vilenjaka: {v.ime}", color=discord.Color.green())
    embed.add_field(name="👤 Razina Vilenjaka", value=f"Lvl {v.nivo} ({v.iskustvo}/100 XP)", inline=True)
    embed.add_field(name="❄️ Valuta", value=f"{v.snowflakes} Snowflakes", inline=True)
    embed.add_field(name="🎄 Razina Jelke", value=f"Lvl {v.jelka_level}", inline=True)
    embed.add_field(name="✨ Efekti Jelke", value=f"Sjaj: +{sjaj} | Ljepota: +{ljepota} | Bonus: +{bonus}", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def shop(ctx):
    user_id = str(ctx.author.id)
    v = vilenjaci.get(user_id)
    if not v: return
    
    embed = discord.Embed(title="🏪 Vilenjački Blagdanski Shop", description="Odaberi ukrase iz izbornika ispod i izravno ukrasi svoju jelku!", color=discord.Color.gold())
    await ctx.send(embed=embed, view=ShopView(v))

@bot.command()
async def zadaci(ctx):
    user_id = str(ctx.author.id)
    v = vilenjaci.get(user_id)
    if not v: return
    
    embed = discord.Embed(title="📋 Vilenjački poslovi (8h Cooldown)", description="Klikni na gumb ispod posla koji želiš odraditi odmah!", color=discord.Color.blue())
    await ctx.send(embed=embed, view=ZadaciView(v))

@bot.command()
async def jelka(ctx, member: discord.Member = None):
    target = member or ctx.author
    user_id = str(target.id)
    v = vilenjaci.get(user_id)
    
    if not v:
        await ctx.send("🎅 Taj korisnik još nema svoju jelku.")
        return

    sjaj, ljepota, bonus = calculate_stats(v)
    stablo_prikaz = generiraj_jelku_string(v)

    embed = discord.Embed(
        title=f"🎄 Blagdanska Jelka: {target.display_name}",
        description=f"```\n{stablo_prikaz}\n```",
        color=discord.Color.brand_green()
    )
    embed.add_field(name="📈 Statovi", value=f"Level: **{v.jelka_level}** ({v.jelka_xp}/100 XP)\nSjaj: **+{sjaj}** | Ljepota: **+{ljepota}**", inline=True)
    embed.add_field(name="📦 Ukrasi", value=f"Kugle: {len(v.inventory['kugle'])} | Lampice: {len(v.inventory['lampice'])}", inline=True)
    
    await ctx.send(embed=embed)

@bot.command()
async def leaderboard(ctx):
    if not vilenjaci:
        await ctx.send("🎅 Još nema aktivnih vilenjaka na serveru.")
        return
    
    top = sorted(vilenjaci.values(), key=lambda x: (x.jelka_level, x.nivo, x.snowflakes), reverse=True)[:5]
    embed = discord.Embed(title="🏆 TOP 5 Vilenjačkih Jelki", color=discord.Color.red())
    
    for i, v in enumerate(top, 1):
        korisnik = bot.get_user(int(v.user_id))
        ime = korisnik.display_name if korisnik else v.ime
        embed.add_field(name=f"{i}. {ime}", value=f"🎄 Jelka Lvl: **{v.jelka_level}** | Lvl: {v.nivo} | ❄️ {v.snowflakes}", inline=False)
        
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    load_vilenjaci()
    print(f"🎄 {bot.user} je spreman za rad na Railwayu!")

if __name__ == "__main__":
    token = os.environ.get('DISCORD_TOKEN') or "YOUR_TOKEN_HERE"
    bot.run(token)
