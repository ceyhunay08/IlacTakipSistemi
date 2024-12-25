import pyodbc
from datetime import datetime

def connect_to_db():
    try:
        conn = pyodbc.connect(
            "Driver={SQL Server};"
            "Server=ServerName;" 
            "Database=IlacTakipSistemi;"
            "UID=username;"  
            "PWD=Password;"
        )
        print("Veri tabanı bağlantısı başarılı!")
        return conn
    except Exception as e:
        print("Bağlantı hatası:", e)
        return None

#HASTA İŞLEMLERİ

# 1. Hastaları Listeleme

def list_patients(conn):
    cursor = conn.cursor()
    query = "SELECT HastaID, Ad, Soyad, DogumTarihi, Cinsiyet FROM Hastalar"
    cursor.execute(query)
    patients = cursor.fetchall()
    for patient in patients:
        print(patient)

# 2. Hasta Bilgilerini Güncelleme

def update_patient(conn):
    cursor = conn.cursor()

    print("Mevcut Hastalar:")
    query = "SELECT HastaID, Ad, Soyad FROM Hastalar"
    cursor.execute(query)
    patients = cursor.fetchall()

    for patient in patients:
        print(f"Hasta ID: {patient.HastaID}, İsim: {patient.Ad} {patient.Soyad}")

    hasta_id = int(input("Güncellemek istediğiniz Hasta ID'sini seçiniz: "))

    print("Yeni Bilgileri Giriniz:")
    yeni_ad = input("Ad: ").strip().capitalize()
    yeni_soyad = input("Soyad: ").strip().capitalize()
    yeni_dogum_tarihi = input("Doğum Tarihi (YYYY-AA-GG): ").strip()
    yeni_cinsiyet = input("Cinsiyet (Erkek/Kadın): ").strip().capitalize()

    query = """
        UPDATE Hastalar
        SET Ad = ?, Soyad = ?, DogumTarihi = ?, Cinsiyet = ?
        WHERE HastaID = ?
    """
    cursor.execute(query, (yeni_ad, yeni_soyad, yeni_dogum_tarihi, yeni_cinsiyet, hasta_id))
    conn.commit()

    print(f"Hasta ID {hasta_id} başarıyla güncellendi!")


#REÇETE İŞLEMLERİ

# 1. Reçete Ekleme Başlangıç
def start_prescription_process(conn):
    cursor = conn.cursor()

    print("Mevcut Hastalar:")
    query = "SELECT HastaID, Ad, Soyad FROM Hastalar"
    cursor.execute(query)
    patients = cursor.fetchall()

    for patient in patients:
        print(f"Hasta ID: {patient.HastaID}, İsim: {patient.Ad} {patient.Soyad}")

    print("Yeni Hastaya Reçete Kaydı İçin: '0', Mevcut Hastaya Reçete Kaydı için Hasta ID giriniz.")
    secim = int(input("Lütfen bir seçenek giriniz: "))

    if secim == 0:  # Yeni hasta ekleme
        print("Yeni Hasta Bilgilerini Giriniz:")
        ad = input("Ad: ").strip().capitalize()
        soyad = input("Soyad: ").strip().capitalize()
        dogum_tarihi = input("Doğum Tarihi (YYYY-AA-GG): ").strip()
        cinsiyet = input("Cinsiyet (Erkek/Kadın): ").strip().capitalize()

        query = """
            INSERT INTO Hastalar (Ad, Soyad, DogumTarihi, Cinsiyet)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (ad, soyad, dogum_tarihi, cinsiyet))
        conn.commit()

        cursor.execute("SELECT MAX(HastaID) FROM Hastalar")
        hasta_id = cursor.fetchone()[0]
        print(f"Yeni hasta eklendi! Hasta ID: {hasta_id}")
    else:  
        hasta_id = secim

    # Reçete ekleme işlemi
    add_prescription_with_details(conn, hasta_id)

# 2. Reçete ekleme işlemi
def add_prescription_with_details(conn, hasta_id):
    cursor = conn.cursor()

    doktor_id = select_doktor_id(conn)

    query = "SELECT HastaneID FROM Doktorlar WHERE DoktorID = ?"
    cursor.execute(query, (doktor_id,))
    hastane_id = cursor.fetchone()

    if not hastane_id:
        print("Seçilen doktorun bir hastane kaydı bulunamadı!")
        return
    hastane_id = hastane_id[0]

    from datetime import datetime
    tarih = datetime.now().strftime('%Y-%m-%d')

    prescription_query = """
        INSERT INTO Receteler (HastaID, DoktorID, HastaneID, Tarih)
        VALUES (?, ?, ?, ?)
    """
    cursor.execute(prescription_query, (hasta_id, doktor_id, hastane_id, tarih))
    conn.commit()

    cursor.execute("SELECT MAX(ReceteID) FROM Receteler")
    recete_id = cursor.fetchone()[0]
    print(f"Reçete eklendi! ReçeteID: {recete_id}, Tarih: {tarih}")

    # Reçete detayları ekleme
    add_prescription_details_with_stok(conn, recete_id)

# 3. Reçete detayları ekleme
def add_prescription_details_with_stok(conn, recete_id):
    while True:
        ilac_id = select_ilac_id(conn)
        miktar = int(input("Miktar: "))

        cursor = conn.cursor()
        detail_query = """
            INSERT INTO ReceteDetaylari (ReceteID, IlacID, Miktar)
            VALUES (?, ?, ?)
        """
        cursor.execute(detail_query, (recete_id, ilac_id, miktar))
        conn.commit()
        print(f"ReçeteID {recete_id} için ilaç başarıyla eklendi!")

        eczane_id = select_eczane_id(conn)
        update_eczane_stok(conn, eczane_id, ilac_id, miktar)

        devam = input("Başka ilaç eklemek istiyor musunuz? (E/H): ").strip().lower()
        if devam != "e":
            break

# Hastaları listeleme ve seçim
def select_hasta_id(conn):
    cursor = conn.cursor()
    query = "SELECT HastaID, Ad, Soyad FROM Hastalar"
    cursor.execute(query)
    patients = cursor.fetchall()

    print("Mevcut Hastalar:")
    for patient in patients:
        print(f"Hasta ID: {patient.HastaID}, İsim: {patient.Ad} {patient.Soyad}")

    hasta_id = int(input("Hasta ID seçiniz: "))
    return hasta_id


# Doktorları listeleme ve seçim
def select_doktor_id(conn):
    cursor = conn.cursor()
    query = "SELECT DoktorID, Ad, Soyad, UzmanlikAlani FROM Doktorlar"
    cursor.execute(query)
    doctors = cursor.fetchall()

    print("Mevcut Doktorlar:")
    for doctor in doctors:
        print(f"Doktor ID: {doctor.DoktorID}, İsim: {doctor.Ad} {doctor.Soyad}, Uzmanlık: {doctor.UzmanlikAlani}")

    doktor_id = int(input("Doktor ID seçiniz: "))
    return doktor_id


# Hastaneleri listeleme ve seçim
def select_hastane_id(conn):
    cursor = conn.cursor()
    query = "SELECT HastaneID, HastaneAdi FROM Hastaneler"
    cursor.execute(query)
    hospitals = cursor.fetchall()

    print("Mevcut Hastaneler:")
    for hospital in hospitals:
        print(f"Hastane ID: {hospital.HastaneID}, Hastane Adı: {hospital.HastaneAdi}")

    hastane_id = int(input("Hastane ID seçiniz: "))
    return hastane_id


# İlaçları listeleme ve seçim
def select_ilac_id(conn):
    cursor = conn.cursor()
    query = "SELECT IlacID, IlacAdi FROM Ilaclar"
    cursor.execute(query)
    medicines = cursor.fetchall()

    print("Mevcut İlaçlar:")
    for medicine in medicines:
        print(f"İlaç ID: {medicine.IlacID}, İlaç Adı: {medicine.IlacAdi}")

    ilac_id = int(input("İlaç ID seçiniz: "))
    return ilac_id


# Eczaneleri listeleme ve seçim
def select_eczane_id(conn):
    cursor = conn.cursor()
    query = "SELECT EczaneID, EczaneAdi FROM Eczaneler"
    cursor.execute(query)
    pharmacies = cursor.fetchall()

    print("Mevcut Eczaneler:")
    for pharmacy in pharmacies:
        print(f"Eczane ID: {pharmacy.EczaneID}, Eczane Adı: {pharmacy.EczaneAdi}")

    eczane_id = int(input("Eczane ID seçiniz: "))
    return eczane_id


# Stok azaltma ve uyarı
def update_eczane_stok(conn, eczane_id, ilac_id, miktar):
    cursor = conn.cursor()

    query = "SELECT StokMiktari, MinimumStokSeviyesi FROM EczaneStoklari WHERE EczaneID = ? AND IlacID = ?"
    cursor.execute(query, (eczane_id, ilac_id))
    stok = cursor.fetchone()

    if not stok:
        print(f"Eczane ID {eczane_id} için İlaç ID {ilac_id} stok bilgisi bulunamadı!")
        return

    stok_miktari, minimum_stok = stok

    yeni_stok = stok_miktari - miktar
    if yeni_stok < 0:
        print("Hata: Stok yetersiz!")
        return

    update_query = "UPDATE EczaneStoklari SET StokMiktari = ? WHERE EczaneID = ? AND IlacID = ?"
    cursor.execute(update_query, (yeni_stok, eczane_id, ilac_id))
    conn.commit()

    print(f"Eczane ID {eczane_id}, İlaç"
          f"ID {ilac_id} için stok güncellendi. Yeni Stok: {yeni_stok}")

    if yeni_stok < minimum_stok:
        print(f"Uyarı: Eczane ID {eczane_id}, İlaç ID {ilac_id} stok miktarı minimum seviyenin altına düştü!")

#ECZANE İŞLEMLERİ

# Eczane Stok Artırma

def update_pharmacy_stock(conn):
    cursor = conn.cursor()

    print("Minimum stok seviyesinin altındaki ilaçlar:")
    query = """
        SELECT e.EczaneAdi, i.IlacAdi, es.StokMiktari, es.MinimumStokSeviyesi
        FROM EczaneStoklari es
        JOIN Eczaneler e ON es.EczaneID = e.EczaneID
        JOIN Ilaclar i ON es.IlacID = i.IlacID
        WHERE es.StokMiktari < es.MinimumStokSeviyesi
    """
    cursor.execute(query)
    low_stock_items = cursor.fetchall()

    if low_stock_items:
        for item in low_stock_items:
            print(f"Eczane: {item.EczaneAdi}, İlaç: {item.IlacAdi}, Stok: {item.StokMiktari}, Minimum Stok: {item.MinimumStokSeviyesi}")
    else:
        print("Tüm stoklar minimum seviyenin üzerinde.")

    print("\nEczane stok güncelleme işlemi:")

    query = "SELECT EczaneID, EczaneAdi FROM Eczaneler"
    cursor.execute(query)
    pharmacies = cursor.fetchall()

    print("Mevcut Eczaneler:")
    for pharmacy in pharmacies:
        print(f"Eczane ID: {pharmacy.EczaneID}, Eczane Adı: {pharmacy.EczaneAdi}")

    eczane_id = int(input("Stok güncellemek istediğiniz Eczane ID'sini seçiniz: "))

    query = """
        SELECT es.IlacID, i.IlacAdi, es.StokMiktari 
        FROM EczaneStoklari es
        JOIN Ilaclar i ON es.IlacID = i.IlacID
        WHERE es.EczaneID = ?
    """
    cursor.execute(query, (eczane_id,))
    medicines = cursor.fetchall()

    if not medicines:
        print("Bu eczane için kayıtlı ilaç bulunamadı!")
        return

    print("\nMevcut İlaçlar:")
    for medicine in medicines:
        print(f"İlaç ID: {medicine.IlacID}, İlaç Adı: {medicine.IlacAdi}, Mevcut Stok: {medicine.StokMiktari}")

    ilac_id = int(input("Güncellemek istediğiniz İlaç ID'sini seçiniz: "))
    miktar = int(input("Eklemek istediğiniz miktarı giriniz: "))

    query = """
        UPDATE EczaneStoklari
        SET StokMiktari = StokMiktari + ?
        WHERE EczaneID = ? AND IlacID = ?
    """
    cursor.execute(query, (miktar, eczane_id, ilac_id))
    conn.commit()

    print(f"Eczane ID {eczane_id} için İlaç ID {ilac_id} stok miktarı {miktar} artırıldı.")

# Veri tabanı bağlantısını başlat
connection = connect_to_db()

if connection:

    # Reçete Ekleme
     start_prescription_process(connection)

    # Hasta Bilgilerini Güncelleme
     update_patient(connection)

    # Hastaları Listeleme
      list_patients(connection)

    # Eczane Stok Güncelleme
     update_pharmacy_stock(connection)

     connection.close()