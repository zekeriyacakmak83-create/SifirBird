import json
import os
import random
import sys
import pygame

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()

# --- PERFORMANS VE AĞIR ÇEKİM ÇÖZÜMÜ ---
# Oyun mantığını sabit 400x700 çözünürlükte koşturuyoruz, böylece telefon asla kasmaz!
MANTIK_GENISLIK = 400
MANTIK_YUKSEKLIK = 700

ekran = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
gercek_genislik, gercek_yukseklik = ekran.get_size()

# Ekrana ölçekleme yapacağımız sanal yüzey
oyun_yuzeyi = pygame.Surface((MANTIK_GENISLIK, MANTIK_YUKSEKLIK))
pygame.display.set_caption("SıfırBird")

saat = pygame.time.Clock()
fps = 60

font = pygame.font.Font(None, 30)
kucuk_font = pygame.font.Font(None, 18)
en_kucuk_font = pygame.font.Font(None, 14)


def muzik_cal(dosya_adi, dongu=0):
  try:
    pygame.mixer.music.load(dosya_adi)
    pygame.mixer.music.play(dongu)
  except pygame.error:
    pass


def ses_yukle(dosya_adi):
  try:
    return pygame.mixer.Sound(dosya_adi)
  except:

    class BosSes:

      def play(self):
        pass

    return BosSes()


skor_sesi = ses_yukle("skor.wav")  # Android için wav/ogg önerilir


def fonlu_yazi_ciz(yuzey, metin, yazi_fontu, renk, x, y):
  siyah = (0, 0, 0)
  yuzey.blit(yazi_fontu.render(metin, True, siyah), (x - 2, y - 2))
  yuzey.blit(yazi_fontu.render(metin, True, siyah), (x + 2, y - 2))
  yuzey.blit(yazi_fontu.render(metin, True, siyah), (x - 2, y + 2))
  yuzey.blit(yazi_fontu.render(metin, True, siyah), (x + 2, y + 2))
  yuzey.blit(yazi_fontu.render(metin, True, renk), (x, y))


def resim_yukle(dosya_adi, boyut):
  try:
    dizin = os.path.dirname(os.path.abspath(__file__))
    tam_yol = os.path.join(dizin, dosya_adi)
    resim = pygame.image.load(tam_yol).convert_alpha()
    return pygame.transform.scale(resim, boyut)
  except:
    yuzey = pygame.Surface(boyut)
    yuzey.fill((50, 50, 50))
    return yuzey


# Görseller artık sabit mantık boyutunda yükleniyor (Kasma biter!)
harita_gorselleri = {
    "mahalle": resim_yukle("mahalle.png", (MANTIK_GENISLIK, MANTIK_YUKSEKLIK)),
    "baraj": resim_yukle("baraj.png", (MANTIK_GENISLIK, MANTIK_YUKSEKLIK)),
    "hapishane": resim_yukle(
        "hapishane.png", (MANTIK_GENISLIK, MANTIK_YUKSEKLIK)
    ),
}

karakter_gorselleri = {
    "savas": resim_yukle("savas.png", (40, 40)),
    "cio": resim_yukle("cio.png", (40, 40)),
    "ozgur": resim_yukle("ozgur.png", (40, 40)),
    "anafor": resim_yukle("anafor.png", (40, 40)),
    "cihat": resim_yukle("cihat.png", (40, 40)),
    "gokhan": resim_yukle("gokhan.png", (40, 40)),
}

harita_iconlari = {
    k: pygame.transform.scale(v, (35, 50)) for k, v in harita_gorselleri.items()
}
karakter_iconlari = {
    k: pygame.transform.scale(v, (40, 40))
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
        "aciklama": "Hayatın boyunca 100.000 skor topla.",
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

KAYIT_DOSYASI = "kayit.json"


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
  if os.path.exists(KAYIT_DOSYASI):
    with open(KAYIT_DOSYASI, "r") as dosya:
      kaydedilen = json.load(dosya)
      for key in varsayilan:
        if key not in kaydedilen:
          kaydedilen[key] = varsayilan[key]
      return kaydedilen
  return varsayilan


def verileri_kaydet(veri):
  with open(KAYIT_DOSYASI, "w") as dosya:
    json.dump(veri, dosya)


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

  kus_y = MANTIK_YUKSEKLIK // 2
  kus_hiz = 0
  boru_x = MANTIK_GENISLIK
  alt_boru_y = random.randint(300, 550)
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


kus_x = 50
kus_yaricap = 20
yercekimi = 0.5
ziplama_gucu = -8

boru_genislik = 70
boru_orijinal = resim_yukle("demir.png", (boru_genislik, 600))
boru_hiz = 4
bosluk = 200

oyunu_sifirla()
oyun_durumu = "menu"
son_skor = 0
sarsinti_suresi = 0

magaza_sekmesi = "karakterler"
gorev_sekmesi = "gorevler"

oyna_butonu = pygame.Rect(100, 230, 200, 50)
magaza_butonu = pygame.Rect(100, 300, 200, 50)
gorev_butonu = pygame.Rect(100, 370, 200, 50)
cikis_butonu = pygame.Rect(100, 440, 200, 50)
geri_butonu = pygame.Rect(10, 10, 80, 40)

tab_sol_butonu = pygame.Rect(30, 70, 160, 40)
tab_sag_butonu = pygame.Rect(210, 70, 160, 40)

muzik_cal("acilis.mp3")

while True:
  # Dokunmatik / Fare oranını hesapla (Ağır çekimi ve tıklama kaymasını önler)
  mouse_raw = pygame.mouse.get_pos()
  olcek = gercek_yukseklik / MANTIK_YUKSEKLIK
  ofset_x = (gercek_genislik - (MANTIK_GENISLIK * olcek)) // 2
  mouse_pos = (
      int((mouse_raw[0] - ofset_x) / olcek),
      int(mouse_raw[1] / olcek),
  )

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

  # Her şeyi önce sanal yüzeye çiziyoruz
  oyun_yuzeyi.fill((0, 0, 0))

  if oyun_durumu == "menu":
    oyun_yuzeyi.blit(
        harita_gorselleri[oyuncu_verisi["secili_harita"]], (0, 0)
    )

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

    pygame.draw.rect(
        oyun_yuzeyi, (50, 205, 50), oyna_butonu, border_radius=10
    )
    pygame.draw.rect(
        oyun_yuzeyi, (255, 140, 0), magaza_butonu, border_radius=10
    )
    pygame.draw.rect(
        oyun_yuzeyi, (70, 130, 180), gorev_butonu, border_radius=10
    )
    pygame.draw.rect(
        oyun_yuzeyi, (220, 20, 60), cikis_butonu, border_radius=10
    )

    oyun_yuzeyi.blit(font.render("OYNA", True, (255, 255, 255)), (160, 240))
    oyun_yuzeyi.blit(font.render("MAĞAZA", True, (255, 255, 255)), (145, 310))
    oyun_yuzeyi.blit(
        font.render("GÖREVLER", True, (255, 255, 255)), (130, 380)
    )
    oyun_yuzeyi.blit(font.render("ÇIKIŞ", True, (255, 255, 255)), (160, 450))

    fonlu_yazi_ciz(
        oyun_yuzeyi, f"Son Skor: {son_skor}", font, (255, 255, 255), 130, 70
    )
    fonlu_yazi_ciz(
        oyun_yuzeyi,
        f"Rekor: {oyuncu_verisi['en_yuksek_skor']}",
        font,
        (50, 255, 50),
        140,
        120,
    )
    fonlu_yazi_ciz(
        oyun_yuzeyi,
        f"Altın: {oyuncu_verisi['altin']}",
        font,
        (255, 215, 0),
        140,
        170,
    )

  elif oyun_durumu == "gorevler":
    oyun_yuzeyi.fill((40, 40, 50))
    pygame.draw.rect(oyun_yuzeyi, (200, 0, 0), geri_butonu, border_radius=5)
    oyun_yuzeyi.blit(
        kucuk_font.render("Geri", True, (255, 255, 255)), (25, 17)
    )
    if tiklandi and geri_butonu.collidepoint(mouse_pos):
      oyun_durumu = "menu"

    renk_sol = (
        (70, 130, 180) if gorev_sekmesi == "gorevler" else (100, 100, 100)
    )
    renk_sag = (
        (70, 130, 180) if gorev_sekmesi == "basarimlar" else (100, 100, 100)
    )
    pygame.draw.rect(oyun_yuzeyi, renk_sol, tab_sol_butonu, border_radius=5)
    pygame.draw.rect(oyun_yuzeyi, renk_sag, tab_sag_butonu, border_radius=5)
    oyun_yuzeyi.blit(
        kucuk_font.render("Görevler", True, (255, 255, 255)), (70, 78)
    )
    oyun_yuzeyi.blit(
        kucuk_font.render("Başarımlar", True, (255, 255, 255)), (245, 78)
    )

    if tiklandi:
      if tab_sol_butonu.collidepoint(mouse_pos):
        gorev_sekmesi = "gorevler"
      elif tab_sag_butonu.collidepoint(mouse_pos):
        gorev_sekmesi = "basarimlar"

    if gorev_sekmesi == "gorevler":
      for i, gorev in enumerate(gorevler_listesi):
        kutu = pygame.Rect(20, 130 + (i * 100), 360, 85)
        pygame.draw.rect(oyun_yuzeyi, (60, 60, 70), kutu, border_radius=8)
        ilerleme = (
            son_skor
            if gorev["id"] == "gorev_1"
            and son_skor < gorev["hedef"]
            else (
                oyuncu_verisi["toplam_kalkan"]
                if gorev["id"] == "gorev_2"
                and oyuncu_verisi["toplam_kalkan"] < gorev["hedef"]
                else (
                    oyuncu_verisi["en_yuksek_skor"]
                    if gorev["id"] == "gorev_3"
                    and oyuncu_verisi["en_yuksek_skor"] < gorev["hedef"]
                    else gorev["hedef"]
                )
            )
        )
        durum = oyuncu_verisi["gorevler"][gorev["id"]]
        oyun_yuzeyi.blit(
            kucuk_font.render(gorev["baslik"], True, (255, 255, 255)),
            (kutu.x + 10, kutu.y + 10),
        )
        oyun_yuzeyi.blit(
            en_kucuk_font.render(
                gorev["aciklama"], True, (200, 200, 200)
            ),
            (kutu.x + 10, kutu.y + 35),
        )
        durum_metni = (
            "Tamamlandı"
            if durum == 2
            else f"İlerleme: {ilerleme}/{gorev['hedef']}"
        )
        renk_durum = (100, 100, 100) if durum == 2 else (255, 215, 0)
        oyun_yuzeyi.blit(
            en_kucuk_font.render(durum_metni, True, renk_durum),
            (kutu.x + 10, kutu.y + 60),
        )

        buton_kutu = pygame.Rect(kutu.x + 230, kutu.y + 20, 120, 45)
        if durum == 0:
          pygame.draw.rect(
              oyun_yuzeyi, (100, 100, 100), buton_kutu, border_radius=5
          )
          metin_yuzey = kucuk_font.render(
              f"{gorev['odul']} Altın", True, (200, 200, 200)
          )
        elif durum == 1:
          pygame.draw.rect(
              oyun_yuzeyi, (50, 205, 50), buton_kutu, border_radius=5
          )
          metin_yuzey = kucuk_font.render(
              "ÖDÜLÜ AL", True, (255, 255, 255)
          )
        else:
          pygame.draw.rect(
              oyun_yuzeyi, (50, 50, 50), buton_kutu, border_radius=5
          )
          metin_yuzey = kucuk_font.render("ALINDI", True, (150, 150, 150))
        oyun_yuzeyi.blit(
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
        kutu = pygame.Rect(20, 130 + (i * 100), 360, 85)
        pygame.draw.rect(oyun_yuzeyi, (70, 50, 50), kutu, border_radius=8)
        ilerleme = min(
            oyuncu_verisi[basarim["degisken"]], basarim["hedef"]
        )
        tamamlandi_mi = ilerleme >= basarim["hedef"]
        oyun_yuzeyi.blit(
            kucuk_font.render(basarim["baslik"], True, (255, 215, 0)),
            (kutu.x + 10, kutu.y + 10),
        )
        oyun_yuzeyi.blit(
            en_kucuk_font.render(
                basarim["aciklama"], True, (200, 200, 200)
            ),
            (kutu.x + 10, kutu.y + 35),
        )
        if tamamlandi_mi:
          fonlu_yazi_ciz(
              oyun_yuzeyi,
              "EFSANE TAMAMLANDI!",
              kucuk_font,
              (50, 255, 50),
              kutu.x + 10,
              kutu.y + 60,
          )
        else:
          oyun_yuzeyi.blit(
              en_kucuk_font.render(
                  f"İlerleme: {ilerleme} / {basarim['hedef']}",
                  True,
                  (255, 255, 255),
              ),
              (kutu.x + 10, kutu.y + 60),
          )
          bar_arkaplan = pygame.Rect(kutu.x + 150, kutu.y + 60, 190, 15)
          pygame.draw.rect(
              oyun_yuzeyi, (30, 30, 30), bar_arkaplan, border_radius=3
          )
          if ilerleme > 0:
            doluluk = (ilerleme / basarim["hedef"]) * 190
            bar_dolu = pygame.Rect(
                kutu.x + 150, kutu.y + 60, int(doluluk), 15
            )
            pygame.draw.rect(
                oyun_yuzeyi, (255, 140, 0), bar_dolu, border_radius=3
            )

  elif oyun_durumu == "magaza":
    oyun_yuzeyi.fill((30, 30, 30))
    pygame.draw.rect(oyun_yuzeyi, (200, 0, 0), geri_butonu, border_radius=5)
    oyun_yuzeyi.blit(
        kucuk_font.render("Geri", True, (255, 255, 255)), (25, 17)
    )
    if tiklandi and geri_butonu.collidepoint(mouse_pos):
      oyun_durumu = "menu"
    fonlu_yazi_ciz(
        oyun_yuzeyi,
        f"Cüzdan: {oyuncu_verisi['altin']} Altın",
        font,
        (255, 215, 0),
        120,
        12,
    )

    renk_sol = (
        (50, 205, 50) if magaza_sekmesi == "karakterler" else (100, 100, 100)
    )
    renk_sag = (
        (50, 205, 50) if magaza_sekmesi == "haritalar" else (100, 100, 100)
    )
    pygame.draw.rect(oyun_yuzeyi, renk_sol, tab_sol_butonu, border_radius=5)
    pygame.draw.rect(oyun_yuzeyi, renk_sag, tab_sag_butonu, border_radius=5)
    oyun_yuzeyi.blit(
        kucuk_font.render("Karakterler", True, (255, 255, 255)), (60, 80)
    )
    oyun_yuzeyi.blit(
        kucuk_font.render("Haritalar", True, (255, 255, 255)), (255, 80)
    )

    if tiklandi:
      if tab_sol_butonu.collidepoint(mouse_pos):
        magaza_sekmesi = "karakterler"
      elif tab_sag_butonu.collidepoint(mouse_pos):
        magaza_sekmesi = "haritalar"

    aktif_liste, aktif_ikonlar, kayit_sahip, kayit_secili = (
        (
            magaza_karakterler,
            karakter_iconlari,
            "sahip_karakterler",
            "secili_karakter",
        )
        if magaza_sekmesi == "karakterler"
        else (magaza_haritalar, harita_iconlari, "sahip_haritalar", "secili_harita")
    )

    for i, urun in enumerate(aktif_liste):
      liste_kutusu = pygame.Rect(20, 130 + (i * 75), 360, 60)
      pygame.draw.rect(oyun_yuzeyi, (50, 50, 50), liste_kutusu, border_radius=8)
      sahip_mi = urun["id"] in oyuncu_verisi[kayit_sahip]
      secili_mi = oyuncu_verisi[kayit_secili] == urun["id"]
      ikon_y = (
          liste_kutusu.y + 10
          if magaza_sekmesi == "karakterler"
          else liste_kutusu.y + 5
      )
      oyun_yuzeyi.blit(
          aktif_ikonlar[urun["id"]], (liste_kutusu.x + 10, ikon_y)
      )
      oyun_yuzeyi.blit(
          font.render(urun["isim"], True, (255, 255, 255)),
          (liste_kutusu.x + 70, liste_kutusu.y + 12),
      )
      buton_kutusu = pygame.Rect(
          liste_kutusu.x + 240, liste_kutusu.y + 10, 110, 40
      )
      buton_renk = (
          (50, 205, 50)
          if secili_mi
          else ((100, 149, 237) if sahip_mi else (220, 20, 60))
      )
      buton_metin = (
          "Seçili"
          if secili_mi
          else ("Seç" if sahip_mi else f"{urun['fiyat']} Altın")
      )
      pygame.draw.rect(oyun_yuzeyi, buton_renk, buton_kutusu, border_radius=5)
      metin_yuzey = kucuk_font.render(buton_metin, True, (255, 255, 255))
      oyun_yuzeyi.blit(
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
        if alt_boru_y > 600:
          boru_hareket_yonu = -1
        elif alt_boru_y < 200:
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

      bg_x -= 1
      if bg_x <= -MANTIK_GENISLIK:
        bg_x = 0

      if random.randint(1, 3) == 1:
        partikuller.append(
            [kus_x - 15, kus_y + random.randint(-10, 10), random.randint(2, 5)]
        )
      for p in partikuller[:]:
        p[0] -= 2
        p[2] -= 0.1
        if p[2] <= 0:
          partikuller.remove(p)

      if boru_x < -boru_genislik:
        boru_x = MANTIK_GENISLIK
        alt_boru_y = random.randint(300, 550)
        skor_alindi = False
        guc_var = (
            True
            if (not kalkan_aktif and random.randint(1, 5) == 1)
            else False
        )
        if guc_var:
          guc_x = MANTIK_GENISLIK + boru_genislik + 50
          guc_y = random.randint(200, 500)
        boru_hareket_yonu = (
            random.choice([-1, 1])
            if (skor >= 5 and random.randint(0, 1) == 1)
            else 0
        )

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
          boru_x, alt_boru_y - bosluk - 600, boru_genislik, 600
      )
      alt_boru_kutu = pygame.Rect(boru_x, alt_boru_y, boru_genislik, 600)

      if (
          kus_kutu.colliderect(ust_boru_kutu)
          or kus_kutu.colliderect(alt_boru_kutu)
          or kus_y > MANTIK_YUKSEKLIK
          or kus_y < 0
      ) and olumsuzluk_suresi == 0:
        if kalkan_aktif and (0 < kus_y < MANTIK_YUKSEKLIK):
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
          muzik_cal("olum.mp3")
          oyun_durumu = "sarsinti"
          sarsinti_suresi = 15

    oyun_yuzeyi.blit(
        harita_gorselleri[oyuncu_verisi["secili_harita"]], (bg_x, 0)
    )
    oyun_yuzeyi.blit(
        harita_gorselleri[oyuncu_verisi["secili_harita"]],
        (bg_x + MANTIK_GENISLIK, 0),
    )
    oyun_yuzeyi.blit(boru_orijinal, (boru_x, alt_boru_y - bosluk - 600))
    oyun_yuzeyi.blit(boru_orijinal, (boru_x, alt_boru_y))

    if guc_var:
      pygame.draw.circle(
          oyun_yuzeyi, (0, 255, 255), (int(guc_x), int(guc_y)), 15
      )
      pygame.draw.circle(
          oyun_yuzeyi, (255, 255, 255), (int(guc_x), int(guc_y)), 8
      )

    for p in partikuller:
      pygame.draw.circle(
          oyun_yuzeyi, (220, 220, 220), (int(p[0]), int(p[1])), int(p[2])
      )

    oyun_yuzeyi.blit(
        karakter_gorselleri[oyuncu_verisi["secili_karakter"]],
        (kus_x - kus_yaricap, int(kus_y) - kus_yaricap),
    )

    if kalkan_aktif:
      pygame.draw.circle(
          oyun_yuzeyi, (0, 255, 255), (int(kus_x), int(kus_y)), kus_yaricap + 5, 3
      )
    elif olumsuzluk_suresi > 0 and (olumsuzluk_suresi % 10 < 5):
      pygame.draw.circle(
          oyun_yuzeyi,
          (255, 50, 50),
          (int(kus_x), int(kus_y)),
          kus_yaricap + 5,
          3,
      )

    skor_metni = str(skor)
    skor_genisligi = font.size(skor_metni)[0]
    fonlu_yazi_ciz(
        oyun_yuzeyi,
        skor_metni,
        font,
        (255, 255, 255),
        (MANTIK_GENISLIK // 2) - (skor_genisligi // 2),
        50,
    )

    if oyun_durumu == "sarsinti":
      sarsinti_suresi -= 1
      sx = random.randint(-10, 10)
      sy = random.randint(-10, 10)
      # Sarsıntıyı ana ekrana ölçekleyerek yansıt
      scaled_surface = pygame.transform.scale(
          oyun_yuzeyi,
          (int(MANTIK_GENISLIK * olcek), int(MANTIK_YUKSEKLIK * olcek)),
      )
      ekran.fill((0, 0, 0))
      ekran.blit(scaled_surface, (ofset_x + sx, sy))
      if sarsinti_suresi <= 0:
        oyun_durumu = "menu"
      pygame.display.update()
      saat.tick(fps)
      continue

  # --- SANAL YÜZEYİ TELEFONA AKICI ŞEKilde ÖLÇEKLEP BAS ---
  scaled_surface = pygame.transform.scale(
      oyun_yuzeyi, (int(MANTIK_GENISLIK * olcek), int(MANTIK_YUKSEKLIK * olcek))
  )
  ekran.fill((0, 0, 0))
  ekran.blit(scaled_surface, (ofset_x, 0))

  pygame.display.update()
  saat.tick(fps)
