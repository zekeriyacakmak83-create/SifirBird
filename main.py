import json
import os
import random
import sys
import pygame

# Android ses gecikmesini ve çökmesini önleyen ideal mixer ayarı
pygame.mixer.pre_init(44100, -16, 2, 1024)
pygame.init()
pygame.mixer.init()

# Çalışma dizinini sabitle (Resim, ses ve kayıt dosyalarının bulunabilmesi için şart)
DIZIN = os.path.dirname(os.path.abspath(__file__))


def tam_yol(dosya_adi):
  return os.path.join(DIZIN, dosya_adi)


# --- EKRAN ORANINI TELEFONA GÖRE OTOMATİK AYARLAMA (TAŞMAYI VE KASMAYI ÖNLER) ---
bilgi = pygame.display.Info()
ekran_orani = (
    bilgi.current_h / bilgi.current_w if bilgi.current_w > 0 else 1.75
)
if ekran_orani < 1:  # Cihaz yatay algılanırsa oranı düzelt
  ekran_orani = bilgi.current_w / bilgi.current_h

genislik = 400
yukseklik = int(genislik * ekran_orani)

# Donanım hızlandırmalı (GPU) tam ekran modu - Sıfır kasma ve sıfır taşma!
try:
  ekran = pygame.display.set_mode(
      (genislik, yukseklik), pygame.SCALED | pygame.FULLSCREEN
  )
except pygame.error:
  ekran = pygame.display.set_mode((genislik, yukseklik))

pygame.display.set_caption("SıfırBird")

saat = pygame.time.Clock()
fps = 60


# --- MODERN VE TÜRKÇE UYUMLU ANDROID FONT YÜKLEYİCİ ---
def font_olustur(boyut, kalin=True):
  for f_adi in ["sans-serif", "roboto", "droidsans", "arial"]:
    try:
      f = pygame.font.SysFont(f_adi, boyut, bold=kalin)
      if f:
        return f
    except:
      continue
  return pygame.font.Font(None, boyut + 6)


font = font_olustur(24, True)
kucuk_font = font_olustur(16, True)
en_kucuk_font = font_olustur(13, False)


# --- TAM YOLLU SES VE MÜZİK FONKSİYONLARI ---
def muzik_cal(dosya_adi, dongu=0):
  try:
    pygame.mixer.music.load(tam_yol(dosya_adi))
    pygame.mixer.music.set_volume(0.8)
    pygame.mixer.music.play(dongu)
  except Exception:
    pass


def ses_yukle(dosya_adi):
  try:
    ses = pygame.mixer.Sound(tam_yol(dosya_adi))
    ses.set_volume(1.0)
    return ses
  except Exception:

    class BosSes:

      def play(self):
        pass

    return BosSes()


skor_sesi = ses_yukle("skor.mp3")
olum_sesi = ses_yukle("olum.mp3")


# Yazıların iç içe geçmesini önleyen temiz gölgeli yazı fonksiyonu
def fonlu_yazi_ciz(yuzey, metin, yazi_fontu, renk, x, y, ortala=False):
  golge = yazi_fontu.render(metin, True, (15, 15, 15))
  ana_metin = yazi_fontu.render(metin, True, renk)
  if ortala:
    x = x - (ana_metin.get_width() // 2)
  yuzey.blit(golge, (x + 2, y + 2))
  yuzey.blit(ana_metin, (x, y))


# Arka planlar için şeffaflıksız (hızlı) yükleme, karakterler için şeffaf yükleme
def resim_yukle(dosya_adi, boyut, seffaf=True):
  try:
    ham_resim = pygame.image.load(tam_yol(dosya_adi))
    resim = ham_resim.convert_alpha() if seffaf else ham_resim.convert()
    return pygame.transform.smoothscale(resim, boyut)
  except Exception:
    yuzey = pygame.Surface(boyut)
    yuzey.fill((50, 50, 50))
    return yuzey


# Arka planlarda seffaf=False kullanarak FPS'i ikiye katlıyoruz
harita_gorselleri = {
    "mahalle": resim_yukle(
        "mahalle.png", (genislik, yukseklik), seffaf=False
    ),
    "baraj": resim_yukle("baraj.png", (genislik, yukseklik), seffaf=False),
    "hapishane": resim_yukle(
        "hapishane.png", (genislik, yukseklik), seffaf=False
    ),
}

karakter_gorselleri = {
    "savas": resim_yukle("savas.png", (42, 42), seffaf=True),
    "cio": resim_yukle("cio.png", (42, 42), seffaf=True),
    "ozgur": resim_yukle("ozgur.png", (42, 42), seffaf=True),
    "anafor": resim_yukle("anafor.png", (42, 42), seffaf=True),
    "cihat": resim_yukle("cihat.png", (42, 42), seffaf=True),
    "gokhan": resim_yukle("gokhan.png", (42, 42), seffaf=True),
}

harita_iconlari = {
    k: pygame.transform.smoothscale(v, (35, 50))
    for k, v in harita_gorselleri.items()
}
karakter_iconlari = {
    k: pygame.transform.smoothscale(v, (40, 40))
    for k, v in karakter_gorselleri.items()
}

gorevler_listesi = [
    {
        "id": "gorev_1",
        "baslik": "Acemi Uçucu",
        "aciklama": "Tek turda 10 skor yap.",
        "odul": 50,
        "hedef": 10,
    },
    {
        "id": "gorev_2",
        "baslik": "Kalkan Ustası",
        "aciklama": "Toplam 3 kalkan topla.",
        "odul": 100,
        "hedef": 3,
    },
    {
        "id": "gorev_3",
        "baslik": "Sıfır Bir Efsanesi",
        "aciklama": "Rekorunu 25 yap.",
        "odul": 200,
        "hedef": 25,
    },
]

basarimlar_listesi = [
    {
        "id": "basarim_1",
        "baslik": "Azrail'in Kankası",
        "aciklama": "Oyunda tam 1000 kere öl.",
        "hedef": 1000,
        "degisken": "toplam_olum",
    },
    {
        "id": "basarim_2",
        "baslik": "Puan Makinesi",
        "aciklama": "Toplam 100.000 skor topla.",
        "hedef": 100000,
        "degisken": "toplam_skor_hayat",
    },
    {
        "id": "basarim_3",
        "baslik": "Kırılmaz İrade",
        "aciklama": "Toplam 100 kere kalkan parçala.",
        "hedef": 100,
        "degisken": "kalkan_kirilma",
    },
]

KAYIT_DOSYASI = tam_yol("kayit.json")


def verileri_yukle():
  varsayilan = {
      "altin": 0,
      "en_yuksek_skor": 0,
      "sahip_haritalar": ["mahalle"],
      "sahip_karakterler": ["savas"],
      "secili_harita": "mahalle",
      "secili_karakter": "savas",
      "toplam_kalkan": 0,
      "gorevler": {"gorev_1": 0, "gorev_2": 0, "gorev_3": 0},
      "toplam_olum": 0,
      "toplam_skor_hayat": 0,
      "kalkan_kirilma": 0,
  }
  try:
    if os.path.exists(KAYIT_DOSYASI):
      with open(KAYIT_DOSYASI, "r", encoding="utf-8") as dosya:
        kaydedilen = json.load(dosya)
        for key in varsayilan:
          if key not in kaydedilen:
            kaydedilen[key] = varsayilan[key]
        return kaydedilen
  except Exception:
    pass
  return varsayilan


def verileri_kaydet(veri):
  try:
    with open(KAYIT_DOSYASI, "w", encoding="utf-8") as dosya:
      json.dump(veri, dosya)
  except Exception:
    pass


oyuncu_verisi = verileri_yukle()

magaza_haritalar = [
    {"id": "mahalle", "isim": "Mahalle", "fiyat": 0},
    {"id": "baraj", "isim": "Baraj", "fiyat": 50},
    {"id": "hapishane", "isim": "Hapis", "fiyat": 100},
]

magaza_karakterler = [
    {"id": "savas", "isim": "Savaş", "fiyat": 0},
    {"id": "cio", "isim": "Cio", "fiyat": 50},
    {"id": "ozgur", "isim": "Özgür", "fiyat": 100},
    {"id": "anafor", "isim": "Anafor", "fiyat": 150},
    {"id": "cihat", "isim": "Cihat", "fiyat": 200},
    {"id": "gokhan", "isim": "Gökhan", "fiyat": 250},
]


def oyunu_sifirla():
  global kus_y, kus_hiz, boru_x, alt_boru_y, skor, skor_alindi, bg_x, partikuller, boru_hareket_yonu
  global kalkan_aktif, olumsuzluk_suresi, guc_var, guc_x, guc_y

  kus_y = yukseklik // 2
  kus_hiz = 0
  boru_x = genislik
  alt_boru_y = random.randint(280, yukseklik - 150)
  skor = 0
  skor_alindi = False
  bg_x = 0
  partikuller = []
  boru_hareket_yonu = 0

  kalkan_aktif = False
  olumsuzluk_suresi = 0
  guc_var = False
  guc_x = 0
  guc_y = 0


kus_x = 65
kus_yaricap = 20
yercekimi = 0.52
ziplama_gucu = -8.5

boru_genislik = 70
boru_boyu = max(700, yukseklik)
boru_orijinal = resim_yukle(
    "demir.png", (boru_genislik, boru_boyu), seffaf=True
)
boru_hiz = 4.5
bosluk = 190

oyun_yuzeyi = pygame.Surface((genislik, yukseklik))

oyunu_sifirla()
oyun_durumu = "menu"
son_skor = 0
sarsinti_suresi = 0

magaza_sekmesi = "karakterler"
gorev_sekmesi = "gorevler"

oyna_butonu = pygame.Rect(100, 240, 200, 50)
magaza_butonu = pygame.Rect(100, 310, 200, 50)
gorev_butonu = pygame.Rect(100, 380, 200, 50)
cikis_butonu = pygame.Rect(100, 450, 200, 50)
geri_butonu = pygame.Rect(15, 20, 80, 40)

tab_sol_butonu = pygame.Rect(20, 75, 175, 42)
tab_sag_butonu = pygame.Rect(205, 75, 175, 42)

muzik_cal("acilis.mp3", -1)

while True:
  mouse_pos = pygame.mouse.get_pos()
  tiklandi = False

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      sys.exit()

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
      tiklandi = True

    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
      if oyun_durumu == "oyun":
        kus_hiz = ziplama_gucu

  if oyun_durumu == "menu":
    ekran.blit(harita_gorselleri[oyuncu_verisi["secili_harita"]], (0, 0))

    if tiklandi:
      if oyna_butonu.collidepoint(mouse_pos):
        oyunu_sifirla()
        oyun_durumu = "oyun"
        pygame.mixer.music.stop()
      elif magaza_butonu.collidepoint(mouse_pos):
        oyun_durumu = "magaza"
      elif gorev_butonu.collidepoint(mouse_pos):
        oyun_durumu = "gorevler"
      elif cikis_butonu.collidepoint(mouse_pos):
        pygame.quit()
        sys.exit()

    for btn, rnk, yazi in [
        (oyna_butonu, (46, 204, 113), "OYNA"),
        (magaza_butonu, (243, 156, 18), "MAĞAZA"),
        (gorev_butonu, (52, 152, 219), "GÖREVLER"),
        (cikis_butonu, (231, 76, 60), "ÇIKIŞ"),
    ]:
      pygame.draw.rect(
          ekran,
          (20, 20, 20),
          (btn.x + 2, btn.y + 3, btn.width, btn.height),
          border_radius=12,
      )
      pygame.draw.rect(ekran, rnk, btn, border_radius=12)
      y_yuzey = font.render(yazi, True, (255, 255, 255))
      ekran.blit(
          y_yuzey,
          (
              btn.centerx - y_yuzey.get_width() // 2,
              btn.centery - y_yuzey.get_height() // 2,
          ),
      )

    # Üst bilgi paneli (Yazıların arka planda kaybolmasını önler)
    panel = pygame.Surface((240, 145), pygame.SRCALPHA)
    pygame.draw.rect(panel, (0, 0, 0, 140), (0, 0, 240, 145), border_radius=15)
    ekran.blit(panel, (80, 65))

    fonlu_yazi_ciz(
        ekran,
        f"Son Skor: {son_skor}",
        font,
        (255, 255, 255),
        genislik // 2,
        80,
        ortala=True,
    )
    fonlu_yazi_ciz(
        ekran,
        f"Rekor: {oyuncu_verisi['en_yuksek_skor']}",
        font,
        (46, 204, 113),
        genislik // 2,
        120,
        ortala=True,
    )
    fonlu_yazi_ciz(
        ekran,
        f"Altın: {oyuncu_verisi['altin']}",
        font,
        (241, 196, 15),
        genislik // 2,
        160,
        ortala=True,
    )

  elif oyun_durumu == "gorevler":
    ekran.fill((30, 34, 42))

    pygame.draw.rect(ekran, (231, 76, 60), geri_butonu, border_radius=8)
    geri_yazi = kucuk_font.render("Geri", True, (255, 255, 255))
    ekran.blit(
        geri_yazi,
        (
            geri_butonu.centerx - geri_yazi.get_width() // 2,
            geri_butonu.centery - geri_yazi.get_height() // 2,
        ),
    )
    if tiklandi and geri_butonu.collidepoint(mouse_pos):
      oyun_durumu = "menu"

    renk_sol = (
        (52, 152, 219) if gorev_sekmesi == "gorevler" else (70, 75, 85)
    )
    renk_sag = (
        (52, 152, 219) if gorev_sekmesi == "basarimlar" else (70, 75, 85)
    )

    pygame.draw.rect(ekran, renk_sol, tab_sol_butonu, border_radius=8)
    pygame.draw.rect(ekran, renk_sag, tab_sag_butonu, border_radius=8)

    sol_yazi = kucuk_font.render("Görevler", True, (255, 255, 255))
    sag_yazi = kucuk_font.render("Başarımlar", True, (255, 255, 255))
    ekran.blit(
        sol_yazi,
        (
            tab_sol_butonu.centerx - sol_yazi.get_width() // 2,
            tab_sol_butonu.centery - sol_yazi.get_height() // 2,
        ),
    )
    ekran.blit(
        sag_yazi,
        (
            tab_sag_butonu.centerx - sag_yazi.get_width() // 2,
            tab_sag_butonu.centery - sag_yazi.get_height() // 2,
        ),
    )

    if tiklandi:
      if tab_sol_butonu.collidepoint(mouse_pos):
        gorev_sekmesi = "gorevler"
      elif tab_sag_butonu.collidepoint(mouse_pos):
        gorev_sekmesi = "basarimlar"

    if gorev_sekmesi == "gorevler":
      for i, gorev in enumerate(gorevler_listesi):
        kutu = pygame.Rect(15, 135 + (i * 100), 370, 88)
        pygame.draw.rect(ekran, (45, 50, 62), kutu, border_radius=10)

        if gorev["id"] == "gorev_1":
          ilerleme = min(son_skor, gorev["hedef"])
        elif gorev["id"] == "gorev_2":
          ilerleme = min(oyuncu_verisi["toplam_kalkan"], gorev["hedef"])
        else:
          ilerleme = min(oyuncu_verisi["en_yuksek_skor"], gorev["hedef"])

        durum = oyuncu_verisi["gorevler"][gorev["id"]]

        ekran.blit(
            kucuk_font.render(gorev["baslik"], True, (255, 255, 255)),
            (kutu.x + 12, kutu.y + 10),
        )
        ekran.blit(
            en_kucuk_font.render(
                gorev["aciklama"], True, (200, 205, 215)
            ),
            (kutu.x + 12, kutu.y + 36),
        )

        durum_metni = (
            "Tamamlandı"
            if durum == 2
            else f"İlerleme: {ilerleme} / {gorev['hedef']}"
        )
        renk_durum = (130, 135, 145) if durum == 2 else (241, 196, 15)
        ekran.blit(
            en_kucuk_font.render(durum_metni, True, renk_durum),
            (kutu.x + 12, kutu.y + 62),
        )

        buton_kutu = pygame.Rect(kutu.right - 120, kutu.y + 22, 108, 44)
        if durum == 0:
          pygame.draw.rect(
              ekran, (80, 85, 95), buton_kutu, border_radius=8
          )
          metin_yuzey = kucuk_font.render(
              f"{gorev['odul']} Altın", True, (210, 210, 210)
          )
        elif durum == 1:
          pygame.draw.rect(
              ekran, (46, 204, 113), buton_kutu, border_radius=8
          )
          metin_yuzey = kucuk_font.render(
              "ÖDÜLÜ AL", True, (255, 255, 255)
          )
        else:
          pygame.draw.rect(
              ekran, (35, 40, 50), buton_kutu, border_radius=8
          )
          metin_yuzey = kucuk_font.render(
              "ALINDI", True, (130, 130, 130)
          )

        ekran.blit(
            metin_yuzey,
            (
                buton_kutu.centerx - metin_yuzey.get_width() // 2,
                buton_kutu.centery - metin_yuzey.get_height() // 2,
            ),
        )

        if tiklandi and buton_kutu.collidepoint(mouse_pos) and durum == 1:
          oyuncu_verisi["altin"] += gorev["odul"]
          oyuncu_verisi["gorevler"][gorev["id"]] = 2
          verileri_kaydet(oyuncu_verisi)

    elif gorev_sekmesi == "basarimlar":
      for i, basarim in enumerate(basarimlar_listesi):
        kutu = pygame.Rect(15, 135 + (i * 100), 370, 88)
        pygame.draw.rect(ekran, (55, 42, 48), kutu, border_radius=10)

        ilerleme = min(
            oyuncu_verisi[basarim["degisken"]], basarim["hedef"]
        )
        tamamlandi_mi = ilerleme >= basarim["hedef"]

        ekran.blit(
            kucuk_font.render(basarim["baslik"], True, (241, 196, 15)),
            (kutu.x + 12, kutu.y + 10),
        )
        ekran.blit(
            en_kucuk_font.render(
                basarim["aciklama"], True, (210, 210, 210)
            ),
            (kutu.x + 12, kutu.y + 35),
        )

        if tamamlandi_mi:
          fonlu_yazi_ciz(
              ekran,
              "EFSANE TAMAMLANDI!",
              kucuk_font,
              (46, 204, 113),
              kutu.x + 12,
              kutu.y + 60,
          )
        else:
          ilerleme_yazi = en_kucuk_font.render(
              f"{ilerleme} / {basarim['hedef']}", True, (255, 255, 255)
          )
          ekran.blit(ilerleme_yazi, (kutu.x + 12, kutu.y + 60))

          bar_x = kutu.x + 135
          bar_gen = kutu.width - 150
          bar_arkaplan = pygame.Rect(bar_x, kutu.y + 62, bar_gen, 14)
          pygame.draw.rect(
              ekran, (25, 20, 25), bar_arkaplan, border_radius=6
          )

          if ilerleme > 0:
            doluluk = max(4, int((ilerleme / basarim["hedef"]) * bar_gen))
            bar_dolu = pygame.Rect(bar_x, kutu.y + 62, doluluk, 14)
            pygame.draw.rect(
                ekran, (243, 156, 18), bar_dolu, border_radius=6
            )

  elif oyun_durumu == "magaza":
    ekran.fill((28, 30, 36))

    pygame.draw.rect(ekran, (231, 76, 60), geri_butonu, border_radius=8)
    geri_yazi = kucuk_font.render("Geri", True, (255, 255, 255))
    ekran.blit(
        geri_yazi,
        (
            geri_butonu.centerx - geri_yazi.get_width() // 2,
            geri_butonu.centery - geri_yazi.get_height() // 2,
        ),
    )
    if tiklandi and geri_butonu.collidepoint(mouse_pos):
      oyun_durumu = "menu"

    fonlu_yazi_ciz(
        ekran,
        f"Cüzdan: {oyuncu_verisi['altin']} Altın",
        font,
        (241, 196, 15),
        115,
        25,
    )

    renk_sol = (
        (46, 204, 113)
        if magaza_sekmesi == "karakterler"
        else (70, 75, 85)
    )
    renk_sag = (
        (46, 204, 113) if magaza_sekmesi == "haritalar" else (70, 75, 85)
    )

    pygame.draw.rect(ekran, renk_sol, tab_sol_butonu, border_radius=8)
    pygame.draw.rect(ekran, renk_sag, tab_sag_butonu, border_radius=8)

    sol_yazi = kucuk_font.render("Karakterler", True, (255, 255, 255))
    sag_yazi = kucuk_font.render("Haritalar", True, (255, 255, 255))
    ekran.blit(
        sol_yazi,
        (
            tab_sol_butonu.centerx - sol_yazi.get_width() // 2,
            tab_sol_butonu.centery - sol_yazi.get_height() // 2,
        ),
    )
    ekran.blit(
        sag_yazi,
        (
            tab_sag_butonu.centerx - sag_yazi.get_width() // 2,
            tab_sag_butonu.centery - sag_yazi.get_height() // 2,
        ),
    )

    if tiklandi:
      if tab_sol_butonu.collidepoint(mouse_pos):
        magaza_sekmesi = "karakterler"
      elif tab_sag_butonu.collidepoint(mouse_pos):
        magaza_sekmesi = "haritalar"

    if magaza_sekmesi == "karakterler":
      aktif_liste = magaza_karakterler
      aktif_ikonlar = karakter_iconlari
      kayit_sahip = "sahip_karakterler"
      kayit_secili = "secili_karakter"
    else:
      aktif_liste = magaza_haritalar
      aktif_ikonlar = harita_iconlari
      kayit_sahip = "sahip_haritalar"
      kayit_secili = "secili_harita"

    for i, urun in enumerate(aktif_liste):
      liste_kutusu = pygame.Rect(15, 130 + (i * 72), 370, 60)
      pygame.draw.rect(ekran, (45, 48, 56), liste_kutusu, border_radius=10)

      sahip_mi = urun["id"] in oyuncu_verisi[kayit_sahip]
      secili_mi = oyuncu_verisi[kayit_secili] == urun["id"]

      ikon_y = (
          liste_kutusu.y + 10
          if magaza_sekmesi == "karakterler"
          else liste_kutusu.y + 5
      )
      ekran.blit(aktif_ikonlar[urun["id"]], (liste_kutusu.x + 12, ikon_y))
      isim_yuzey = font.render(urun["isim"], True, (255, 255, 255))
      ekran.blit(
          isim_yuzey,
          (
              liste_kutusu.x + 65,
              liste_kutusu.centery - isim_yuzey.get_height() // 2,
          ),
      )

      buton_kutusu = pygame.Rect(
          liste_kutusu.right - 120, liste_kutusu.y + 10, 108, 40
      )
      buton_renk = (
          (46, 204, 113)
          if secili_mi
          else ((52, 152, 219) if sahip_mi else (231, 76, 60))
      )
      buton_metin = (
          "Seçili"
          if secili_mi
          else ("Seç" if sahip_mi else f"{urun['fiyat']} Altın")
      )

      pygame.draw.rect(ekran, buton_renk, buton_kutusu, border_radius=8)
      metin_yuzey = kucuk_font.render(buton_metin, True, (255, 255, 255))
      ekran.blit(
          metin_yuzey,
          (
              buton_kutusu.centerx - metin_yuzey.get_width() // 2,
              buton_kutusu.centery - metin_yuzey.get_height() // 2,
          ),
      )

      if tiklandi and buton_kutusu.collidepoint(mouse_pos):
        if sahip_mi:
          oyuncu_verisi[kayit_secili] = urun["id"]
          verileri_kaydet(oyuncu_verisi)
        elif oyuncu_verisi["altin"] >= urun["fiyat"]:
          oyuncu_verisi["altin"] -= urun["fiyat"]
          oyuncu_verisi[kayit_sahip].append(urun["id"])
          oyuncu_verisi[kayit_secili] = urun["id"]
          verileri_kaydet(oyuncu_verisi)

  elif oyun_durumu == "oyun" or oyun_durumu == "sarsinti":
    if oyun_durumu == "oyun":
      if tiklandi:
        kus_hiz = ziplama_gucu

      kus_hiz += yercekimi
      kus_y += kus_hiz
      boru_x -= boru_hiz

      if boru_hareket_yonu != 0:
        alt_boru_y += 2 * boru_hareket_yonu
        if alt_boru_y > yukseklik - 120:
          boru_hareket_yonu = -1
        elif alt_boru_y < 250:
          boru_hareket_yonu = 1

      if guc_var:
        guc_x -= boru_hiz
        guc_kutu = pygame.Rect(guc_x - 15, guc_y - 15, 30, 30)
        kus_kutu = pygame.Rect(
            kus_x - kus_yaricap,
            kus_y - kus_yaricap,
            kus_yaricap * 2,
            kus_yaricap * 2,
        )

        if kus_kutu.colliderect(guc_kutu):
          kalkan_aktif = True
          guc_var = False
          oyuncu_verisi["toplam_kalkan"] += 1
          if (
              oyuncu_verisi["gorevler"]["gorev_2"] == 0
              and oyuncu_verisi["toplam_kalkan"] >= 3
          ):
            oyuncu_verisi["gorevler"]["gorev_2"] = 1
          verileri_kaydet(oyuncu_verisi)

      bg_x -= 1.5
      if bg_x <= -genislik:
        bg_x = 0

      if random.randint(1, 3) == 1:
        partikuller.append(
            [kus_x - 15, kus_y + random.randint(-10, 10), random.randint(2, 5)]
        )

      for p in partikuller[:]:
        p[0] -= 2
        p[2] -= 0.15
        if p[2] <= 0:
          partikuller.remove(p)

      if boru_x < -boru_genislik:
        boru_x = genislik
        alt_boru_y = random.randint(280, yukseklik - 150)
        skor_alindi = False

        if not kalkan_aktif and random.randint(1, 5) == 1:
          guc_var = True
          guc_x = genislik + boru_genislik + 50
          guc_y = random.randint(200, yukseklik - 200)
        else:
          guc_var = False

        if skor >= 5 and random.randint(0, 1) == 1:
          boru_hareket_yonu = random.choice([-1, 1])
        else:
          boru_hareket_yonu = 0

      if kus_x > boru_x + boru_genislik and not skor_alindi:
        skor += 1
        skor_alindi = True
        skor_sesi.play()

        if oyuncu_verisi["gorevler"]["gorev_1"] == 0 and skor >= 10:
          oyuncu_verisi["gorevler"]["gorev_1"] = 1
          verileri_kaydet(oyuncu_verisi)

      if olumsuzluk_suresi > 0:
        olumsuzluk_suresi -= 1

      kus_kutu = pygame.Rect(
          kus_x - kus_yaricap,
          kus_y - kus_yaricap,
          kus_yaricap * 2,
          kus_yaricap * 2,
      )
      ust_boru_kutu = pygame.Rect(
          boru_x, alt_boru_y - bosluk - boru_boyu, boru_genislik, boru_boyu
      )
      alt_boru_kutu = pygame.Rect(
          boru_x, alt_boru_y, boru_genislik, boru_boyu
      )

      if (
          kus_kutu.colliderect(ust_boru_kutu)
          or kus_kutu.colliderect(alt_boru_kutu)
          or kus_y > yukseklik
          or kus_y < 0
      ) and olumsuzluk_suresi == 0:
        if kalkan_aktif and (0 < kus_y < yukseklik):
          kalkan_aktif = False
          olumsuzluk_suresi = 60
          oyuncu_verisi["kalkan_kirilma"] += 1
          verileri_kaydet(oyuncu_verisi)
        else:
          son_skor = skor
          oyuncu_verisi["altin"] += skor
          oyuncu_verisi["toplam_olum"] += 1
          oyuncu_verisi["toplam_skor_hayat"] += skor

          if skor > oyuncu_verisi["en_yuksek_skor"]:
            oyuncu_verisi["en_yuksek_skor"] = skor

          if (
              oyuncu_verisi["gorevler"]["gorev_3"] == 0
              and oyuncu_verisi["en_yuksek_skor"] >= 25
          ):
            oyuncu_verisi["gorevler"]["gorev_3"] = 1

          verileri_kaydet(oyuncu_verisi)
          olum_sesi.play()
          muzik_cal("olum.mp3")
          oyun_durumu = "sarsinti"
          sarsinti_suresi = 15

    # Kasmayı önlemek için normal oyunda doğrudan 'ekran'a, sadece sarsıntıda 'oyun_yuzeyi'ne çiziyoruz
    hedef_yuzey = oyun_yuzeyi if oyun_durumu == "sarsinti" else ekran

    hedef_yuzey.blit(
        harita_gorselleri[oyuncu_verisi["secili_harita"]], (int(bg_x), 0)
    )
    hedef_yuzey.blit(
        harita_gorselleri[oyuncu_verisi["secili_harita"]],
        (int(bg_x) + genislik, 0),
    )

    hedef_yuzey.blit(
        boru_orijinal, (int(boru_x), int(alt_boru_y - bosluk - boru_boyu))
    )
    hedef_yuzey.blit(boru_orijinal, (int(boru_x), int(alt_boru_y)))

    if guc_var:
      pygame.draw.circle(
          hedef_yuzey, (0, 255, 255), (int(guc_x), int(guc_y)), 15
      )
      pygame.draw.circle(
          hedef_yuzey, (255, 255, 255), (int(guc_x), int(guc_y)), 8
      )

    for p in partikuller:
      pygame.draw.circle(
          hedef_yuzey, (220, 220, 220), (int(p[0]), int(p[1])), int(p[2])
      )

    hedef_yuzey.blit(
        karakter_gorselleri[oyuncu_verisi["secili_karakter"]],
        (int(kus_x) - kus_yaricap, int(kus_y) - kus_yaricap),
    )

    if kalkan_aktif:
      pygame.draw.circle(
          hedef_yuzey,
          (0, 255, 255),
          (int(kus_x), int(kus_y)),
          kus_yaricap + 5,
          3,
      )
    elif olumsuzluk_suresi > 0 and (olumsuzluk_suresi % 10 < 5):
      pygame.draw.circle(
          hedef_yuzey,
          (255, 50, 50),
          (int(kus_x), int(kus_y)),
          kus_yaricap + 5,
          3,
      )

    fonlu_yazi_ciz(
        hedef_yuzey,
        str(skor),
        font,
        (255, 255, 255),
        genislik // 2,
        45,
        ortala=True,
    )

    if oyun_durumu == "sarsinti":
      sarsinti_suresi -= 1
      sx = random.randint(-8, 8)
      sy = random.randint(-8, 8)
      ekran.fill((0, 0, 0))
      ekran.blit(oyun_yuzeyi, (sx, sy))

      if sarsinti_suresi <= 0:
        oyun_durumu = "menu"
        muzik_cal("acilis.mp3", -1)

  pygame.display.flip()
  saat.tick(fps)
