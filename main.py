import json
import os
import random
import sys
import pygame

pygame.mixer.pre_init(44100, -16, 2, 1024)
pygame.init()
pygame.mixer.init()

DIZIN = os.path.dirname(os.path.abspath(__file__))


def tam_yol(dosya_adi):
  return os.path.join(DIZIN, dosya_adi)


# --- EKRAN ORANINI TELEFONA GÖRE OTOMATİK AYARLAMA ---
bilgi = pygame.display.Info()
ekran_orani = (
    bilgi.current_h / bilgi.current_w if bilgi.current_w > 0 else 1.75
)
if ekran_orani < 1:
  ekran_orani = bilgi.current_w / bilgi.current_h

genislik = 400
yukseklik = int(genislik * ekran_orani)

try:
  ekran = pygame.display.set_mode(
      (genislik, yukseklik), pygame.SCALED | pygame.FULLSCREEN
  )
except pygame.error:
  ekran = pygame.display.set_mode((genislik, yukseklik))

pygame.display.set_caption("SıfırBird")

saat = pygame.time.Clock()
fps = 60


# --- DAHA BÜYÜK VE NET OKUNUR ANDROID FONTLARI ---
def font_olustur(boyut, kalin=True):
  for f_adi in ["sans-serif", "roboto", "droidsans", "arial"]:
    try:
      f = pygame.font.SysFont(f_adi, boyut, bold=kalin)
      if f:
        return f
    except Exception:
      continue
  return pygame.font.Font(None, boyut + 6)


buyuk_font = font_olustur(34, True)
font = font_olustur(25, True)
kucuk_font = font_olustur(18, True)
en_kucuk_font = font_olustur(15, True)


# --- SES VE MÜZİK FONKSİYONLARI ---
def muzik_cal(dosya_adi, dongu=0):
  try:
    pygame.mixer.music.load(tam_yol(dosya_adi))
    pygame.mixer.music.set_volume(0.9)
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


# --- 8 YÖNLÜ TAM KONTURLU (OUTLINE) SÜPER OKUNUR YAZI FONKSİYONU ---
def net_yazi_ciz(
    yuzey,
    metin,
    yazi_fontu,
    renk,
    x,
    y,
    ortala=False,
    dikey_ortala=False,
    kalinlik=2,
):
  ana_metin = yazi_fontu.render(metin, True, renk)
  dis_metin = yazi_fontu.render(metin, True, (0, 0, 0))

  if ortala:
    x = x - (ana_metin.get_width() // 2)
  if dikey_ortala:
    y = y - (ana_metin.get_height() // 2)

  if kalinlik > 0:
    for dx in (-kalinlik, 0, kalinlik):
      for dy in (-kalinlik, 0, kalinlik):
        if dx != 0 or dy != 0:
          yuzey.blit(dis_metin, (x + dx, y + dy))

  yuzey.blit(ana_metin, (x, y))


def resim_yukle(dosya_adi, boyut, seffaf=True):
  try:
    ham_resim = pygame.image.load(tam_yol(dosya_adi))
    resim = ham_resim.convert_alpha() if seffaf else ham_resim.convert()
    return pygame.transform.smoothscale(resim, boyut)
  except Exception:
    yuzey = pygame.Surface(boyut)
    yuzey.fill((50, 50, 50))
    return yuzey


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

oyna_butonu = pygame.Rect(95, 240, 210, 52)
magaza_butonu = pygame.Rect(95, 310, 210, 52)
gorev_butonu = pygame.Rect(95, 380, 210, 52)
cikis_butonu = pygame.Rect(95, 450, 210, 52)
geri_butonu = pygame.Rect(15, 20, 85, 42)

tab_sol_butonu = pygame.Rect(15, 75, 180, 44)
tab_sag_butonu = pygame.Rect(205, 75, 180, 44)

# SADECE OYUN İLK AÇILDIĞINDA 1 KERE ÇALAR (dongu=0)
muzik_cal("acilis.mp3", 0)

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
          (15, 15, 15),
          (btn.x + 3, btn.y + 4, btn.width, btn.height),
          border_radius=12,
      )
      pygame.draw.rect(ekran, rnk, btn, border_radius=12)
      pygame.draw.rect(ekran, (255, 255, 255), btn, width=2, border_radius=12)
      net_yazi_ciz(
          ekran,
          yazi,
          font,
          (255, 255, 255),
          btn.centerx,
          btn.centery,
          ortala=True,
          dikey_ortala=True,
          kalinlik=2,
      )

    # Koyu ve çerçeveli üst skor tabelası
    panel = pygame.Surface((260, 155), pygame.SRCALPHA)
    pygame.draw.rect(panel, (15, 18, 24, 215), (0, 0, 260, 155), border_radius=16)
    pygame.draw.rect(
        panel, (255, 255, 255, 90), (0, 0, 260, 155), width=2, border_radius=16
    )
    ekran.blit(panel, (70, 60))

    net_yazi_ciz(
        ekran,
        f"Son Skor: {son_skor}",
        font,
        (255, 255, 255),
        genislik // 2,
        78,
        ortala=True,
        kalinlik=2,
    )
    net_yazi_ciz(
        ekran,
        f"Rekor: {oyuncu_verisi['en_yuksek_skor']}",
        font,
        (46, 235, 120),
        genislik // 2,
        122,
        ortala=True,
        kalinlik=2,
    )
    net_yazi_ciz(
        ekran,
        f"Altın: {oyuncu_verisi['altin']}",
        font,
        (255, 215, 0),
        genislik // 2,
        166,
        ortala=True,
        kalinlik=2,
    )

  elif oyun_durumu == "gorevler":
    ekran.fill((22, 26, 34))

    pygame.draw.rect(ekran, (231, 76, 60), geri_butonu, border_radius=8)
    net_yazi_ciz(
        ekran,
        "Geri",
        kucuk_font,
        (255, 255, 255),
        geri_butonu.centerx,
        geri_butonu.centery,
        ortala=True,
        dikey_ortala=True,
        kalinlik=2,
    )
    if tiklandi and geri_butonu.collidepoint(mouse_pos):
      oyun_durumu = "menu"

    renk_sol = (
        (52, 152, 219) if gorev_sekmesi == "gorevler" else (60, 68, 82)
    )
    renk_sag = (
        (52, 152, 219) if gorev_sekmesi == "basarimlar" else (60, 68, 82)
    )

    pygame.draw.rect(ekran, renk_sol, tab_sol_butonu, border_radius=8)
    pygame.draw.rect(ekran, renk_sag, tab_sag_butonu, border_radius=8)

    net_yazi_ciz(
        ekran,
        "Görevler",
        kucuk_font,
        (255, 255, 255),
        tab_sol_butonu.centerx,
        tab_sol_butonu.centery,
        ortala=True,
        dikey_ortala=True,
        kalinlik=2,
    )
    net_yazi_ciz(
        ekran,
        "Başarımlar",
        kucuk_font,
        (255, 255, 255),
        tab_sag_butonu.centerx,
        tab_sag_butonu.centery,
        ortala=True,
        dikey_ortala=True,
        kalinlik=2,
    )

    if tiklandi:
      if tab_sol_butonu.collidepoint(mouse_pos):
        gorev_sekmesi = "gorevler"
      elif tab_sag_butonu.collidepoint(mouse_pos):
        gorev_sekmesi = "basarimlar"

    if gorev_sekmesi == "gorevler":
      for i, gorev in enumerate(gorevler_listesi):
        kutu = pygame.Rect(15, 135 + (i * 105), 370, 92)
        pygame.draw.rect(ekran, (38, 44, 56), kutu, border_radius=10)
        pygame.draw.rect(
            ekran, (85, 95, 115), kutu, width=2, border_radius=10
        )

        if gorev["id"] == "gorev_1":
          ilerleme = min(son_skor, gorev["hedef"])
        elif gorev["id"] == "gorev_2":
          ilerleme = min(oyuncu_verisi["toplam_kalkan"], gorev["hedef"])
        else:
          ilerleme = min(oyuncu_verisi["en_yuksek_skor"], gorev["hedef"])

        durum = oyuncu_verisi["gorevler"][gorev["id"]]

        net_yazi_ciz(
            ekran,
            gorev["baslik"],
            kucuk_font,
            (255, 255, 255),
            kutu.x + 14,
            kutu.y + 10,
            kalinlik=2,
        )
        net_yazi_ciz(
            ekran,
            gorev["aciklama"],
            en_kucuk_font,
            (235, 240, 250),
            kutu.x + 14,
            kutu.y + 38,
            kalinlik=1,
        )

        durum_metni = (
            "Tamamlandı"
            if durum == 2
            else f"İlerleme: {ilerleme} / {gorev['hedef']}"
        )
        renk_durum = (160, 170, 180) if durum == 2 else (255, 215, 0)
        net_yazi_ciz(
            ekran,
            durum_metni,
            en_kucuk_font,
            renk_durum,
            kutu.x + 14,
            kutu.y + 64,
            kalinlik=1,
        )

        buton_kutu = pygame.Rect(kutu.right - 122, kutu.y + 23, 110, 46)
        if durum == 0:
          pygame.draw.rect(
              ekran, (75, 82, 95), buton_kutu, border_radius=8
          )
          b_yazi = f"{gorev['odul']} Altın"
          b_renk = (240, 240, 240)
        elif durum == 1:
          pygame.draw.rect(
              ekran, (46, 204, 113), buton_kutu, border_radius=8
          )
          b_yazi = "ÖDÜLÜ AL"
          b_renk = (255, 255, 255)
        else:
          pygame.draw.rect(
              ekran, (30, 35, 45), buton_kutu, border_radius=8
          )
          b_yazi = "ALINDI"
          b_renk = (160, 160, 160)

        net_yazi_ciz(
            ekran,
            b_yazi,
            kucuk_font,
            b_renk,
            buton_kutu.centerx,
            buton_kutu.centery,
            ortala=True,
            dikey_ortala=True,
            kalinlik=2,
        )

        if tiklandi and buton_kutu.collidepoint(mouse_pos) and durum == 1:
          oyuncu_verisi["altin"] += gorev["odul"]
          oyuncu_verisi["gorevler"][gorev["id"]] = 2
          verileri_kaydet(oyuncu_verisi)

    elif gorev_sekmesi == "basarimlar":
      for i, basarim in enumerate(basarimlar_listesi):
        kutu = pygame.Rect(15, 135 + (i * 105), 370, 92)
        pygame.draw.rect(ekran, (48, 36, 44), kutu, border_radius=10)
        pygame.draw.rect(
            ekran, (110, 80, 95), kutu, width=2, border_radius=10
        )

        ilerleme = min(
            oyuncu_verisi[basarim["degisken"]], basarim["hedef"]
        )
        tamamlandi_mi = ilerleme >= basarim["hedef"]

        net_yazi_ciz(
            ekran,
            basarim["baslik"],
            kucuk_font,
            (255, 215, 0),
            kutu.x + 14,
            kutu.y + 10,
            kalinlik=2,
        )
        net_yazi_ciz(
            ekran,
            basarim["aciklama"],
            en_kucuk_font,
            (240, 240, 240),
            kutu.x + 14,
            kutu.y + 38,
            kalinlik=1,
        )

        if tamamlandi_mi:
          net_yazi_ciz(
              ekran,
              "EFSANE TAMAMLANDI!",
              kucuk_font,
              (46, 235, 120),
              kutu.x + 14,
              kutu.y + 62,
              kalinlik=2,
          )
        else:
          net_yazi_ciz(
              ekran,
              f"{ilerleme} / {basarim['hedef']}",
              en_kucuk_font,
              (255, 255, 255),
              kutu.x + 14,
              kutu.y + 64,
              kalinlik=1,
          )

          bar_x = kutu.x + 145
          bar_gen = kutu.width - 160
          bar_arkaplan = pygame.Rect(bar_x, kutu.y + 66, bar_gen, 15)
          pygame.draw.rect(
              ekran, (20, 15, 20), bar_arkaplan, border_radius=6
          )

          if ilerleme > 0:
            doluluk = max(6, int((ilerleme / basarim["hedef"]) * bar_gen))
            bar_dolu = pygame.Rect(bar_x, kutu.y + 66, doluluk, 15)
            pygame.draw.rect(
                ekran, (243, 156, 18), bar_dolu, border_radius=6
            )

  elif oyun_durumu == "magaza":
    ekran.fill((22, 26, 34))

    pygame.draw.rect(ekran, (231, 76, 60), geri_butonu, border_radius=8)
    net_yazi_ciz(
        ekran,
        "Geri",
        kucuk_font,
        (255, 255, 255),
        geri_butonu.centerx,
        geri_butonu.centery,
        ortala=True,
        dikey_ortala=True,
        kalinlik=2,
    )
    if tiklandi and geri_butonu.collidepoint(mouse_pos):
      oyun_durumu = "menu"

    net_yazi_ciz(
        ekran,
        f"Cüzdan: {oyuncu_verisi['altin']} Altın",
        font,
        (255, 215, 0),
        115,
        26,
        kalinlik=2,
    )

    renk_sol = (
        (46, 204, 113)
        if magaza_sekmesi == "karakterler"
        else (60, 68, 82)
    )
    renk_sag = (
        (46, 204, 113) if magaza_sekmesi == "haritalar" else (60, 68, 82)
    )

    pygame.draw.rect(ekran, renk_sol, tab_sol_butonu, border_radius=8)
    pygame.draw.rect(ekran, renk_sag, tab_sag_butonu, border_radius=8)

    net_yazi_ciz(
        ekran,
        "Karakterler",
        kucuk_font,
        (255, 255, 255),
        tab_sol_butonu.centerx,
        tab_sol_butonu.centery,
        ortala=True,
        dikey_ortala=True,
        kalinlik=2,
    )
    net_yazi_ciz(
        ekran,
        "Haritalar",
        kucuk_font,
        (255, 255, 255),
        tab_sag_butonu.centerx,
        tab_sag_butonu.centery,
        ortala=True,
        dikey_ortala=True,
        kalinlik=2,
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
      liste_kutusu = pygame.Rect(15, 132 + (i * 74), 370, 62)
      pygame.draw.rect(ekran, (38, 44, 56), liste_kutusu, border_radius=10)
      pygame.draw.rect(
          ekran, (80, 90, 110), liste_kutusu, width=2, border_radius=10
      )

      sahip_mi = urun["id"] in oyuncu_verisi[kayit_sahip]
      secili_mi = oyuncu_verisi[kayit_secili] == urun["id"]

      ikon_y = (
          liste_kutusu.y + 11
          if magaza_sekmesi == "karakterler"
          else liste_kutusu.y + 6
      )
      ekran.blit(aktif_ikonlar[urun["id"]], (liste_kutusu.x + 12, ikon_y))
      net_yazi_ciz(
          ekran,
          urun["isim"],
          font,
          (255, 255, 255),
          liste_kutusu.x + 68,
          liste_kutusu.centery,
          dikey_ortala=True,
          kalinlik=2,
      )

      buton_kutusu = pygame.Rect(
          liste_kutusu.right - 122, liste_kutusu.y + 10, 110, 42
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
      net_yazi_ciz(
          ekran,
          buton_metin,
          kucuk_font,
          (255, 255, 255),
          buton_kutusu.centerx,
          buton_kutusu.centery,
          ortala=True,
          dikey_ortala=True,
          kalinlik=2,
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
          oyun_durumu = "sarsinti"
          sarsinti_suresi = 15

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

    net_yazi_ciz(
        hedef_yuzey,
        str(skor),
        buyuk_font,
        (255, 255, 255),
        genislik // 2,
        45,
        ortala=True,
        kalinlik=3,
    )

    if oyun_durumu == "sarsinti":
      sarsinti_suresi -= 1
      sx = random.randint(-8, 8)
      sy = random.randint(-8, 8)
      ekran.fill((0, 0, 0))
      ekran.blit(oyun_yuzeyi, (sx, sy))

      if sarsinti_suresi <= 0:
        oyun_durumu = "menu"

  pygame.display.flip()
  saat.tick(fps)
