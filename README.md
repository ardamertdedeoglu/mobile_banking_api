# 🏦 Mobile Banking API

Flask tabanlı, SQLite veritabanı kullanan bir mobil bankacılık REST API projesidir. Kullanıcı kayıt/giriş, hesap yönetimi, para transferi ve işlem geçmişi gibi temel bankacılık işlevlerini sunar.

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Teknolojiler](#-teknolojiler)
- [Proje Yapısı](#-proje-yapısı)
- [Kurulum](#-kurulum)
- [Çalıştırma](#-çalıştırma)
- [API Endpoint'leri](#-api-endpointleri)
- [Veritabanı Şeması](#-veritabanı-şeması)
- [Tarayıcı Test Paneli](#-tarayıcı-test-paneli)
- [Test Senaryoları](#-test-senaryoları)

---

## ✨ Özellikler

- **Kullanıcı Yönetimi:** E-posta ve şifre ile kayıt olma, giriş yapma ve oturumu kapatma
- **Hesap Yönetimi:** Birden fazla banka hesabı oluşturma (TRY, USD, EUR), hesap listeleme ve hesap detayı görüntüleme
- **Para Transferi:** Hesaplar arası transfer ve para yatırma (deposit) işlemleri — atomik transaction desteğiyle
- **İşlem Geçmişi:** Tarih aralığı filtresiyle işlem sorgulama (DESC sıralı)
- **Yetkilendirme:** Flask session cookie ile oturum yönetimi — login olmadan erişim engeli (401)
- **Tarayıcı Test Paneli:** Tüm endpoint'lerin kolayca test edilebildiği modern web arayüzü

---

## 🛠 Teknolojiler

| Teknoloji | Kullanım |
|-----------|----------|
| Python 3.10+ | Backend dili |
| Flask | Web framework |
| SQLite | Veritabanı (tek dosya: `bank.db`) |
| bcrypt | Şifre hashleme |
| python-dotenv | Ortam değişkenleri yönetimi |
| Jinja2 | HTML template rendering |

---

## 📁 Proje Yapısı

```
mobile_banking_api/
├── app.py                  # Ana uygulama — route tanımları
├── db.py                   # Veritabanı bağlantısı ve tablo oluşturma
├── requirements.txt        # Python bağımlılıkları
├── .env                    # Ortam değişkenleri (SECRET_KEY)
├── .gitignore              # Git tarafından yok sayılan dosyalar
├── bank.db                 # SQLite veritabanı (otomatik oluşturulur)
├── services/               # İş mantığı katmanı
│   ├── auth.py             # Kayıt, giriş, çıkış servisleri
│   ├── accounts.py         # Hesap oluşturma, listeleme, detay servisleri
│   ├── transfer.py         # Transfer ve deposit servisleri
│   └── transactions.py     # İşlem geçmişi servisi
└── templates/
    └── index.html          # Tarayıcı test paneli (API dashboard)
```

---

## 🚀 Kurulum

### 1. Depoyu klonlayın

```bash
git clone <repo-url>
cd mobile_banking_api
```

### 2. Sanal ortam oluşturun ve aktifleştirin

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### 3. Bağımlılıkları yükleyin

```bash
pip install -r requirements.txt
```

### 4. Ortam değişkenlerini ayarlayın

Proje kök dizininde bir `.env` dosyası oluşturun. Şablon olarak `.env.example` dosyasını kullanabilirsiniz:

```bash
cp .env.example .env
```

Ardından `.env` dosyasını açıp `SECRET_KEY` değerini kendi gizli anahtarınızla güncelleyin. Rastgele bir anahtar oluşturmak için:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## ▶️ Çalıştırma

```bash
# Sanal ortamın aktif olduğundan emin olun
source .venv/bin/activate

# Uygulamayı başlatın
python3 app.py
```

Uygulama varsayılan olarak **http://127.0.0.1:5000** adresinde başlayacaktır.

> **Not:** macOS'ta 5000 portu AirPlay Receiver tarafından kullanılıyor olabilir. Bu durumda System Settings > AirDrop & Handoff > AirPlay Receiver seçeneğini kapatabilir veya uygulamayı farklı bir portta çalıştırabilirsiniz:
> ```bash
> flask run --port 5001
> ```

Veritabanı tabloları (`users`, `accounts`, `transactions`) ilk bağlantıda **otomatik olarak oluşturulur**. Ayrı bir migration adımı gerekmez.

---

## 📡 API Endpoint'leri

### Auth (Kimlik Doğrulama)

| Method | Endpoint | Açıklama | Auth |
|--------|----------|----------|------|
| POST | `/api/auth/register` | Yeni kullanıcı kaydı | ❌ |
| POST | `/api/auth/login` | Kullanıcı girişi | ❌ |
| GET | `/logout` | Oturumu kapat | ❌ |

#### `POST /api/auth/register`

```json
{
  "email": "kullanici@ornek.com",
  "password": "guvenli_sifre_123"
}
```

**Kurallar:**
- `email` benzersiz olmalıdır (aynı e-posta ile tekrar kayıt → 409)
- `password` minimum 12 karakter olmalıdır

**Başarılı yanıt (201):**
```json
{
  "created_at": "2026-07-10 14:30:00",
  "email": "kullanici@ornek.com",
  "success": "true"
}
```

#### `POST /api/auth/login`

```json
{
  "email": "kullanici@ornek.com",
  "password": "guvenli_sifre_123"
}
```

**Başarılı yanıt (200):**
```json
{
  "session": 1,
  "success": "true"
}
```

---

### Accounts (Hesaplar)

| Method | Endpoint | Açıklama | Auth |
|--------|----------|----------|------|
| GET | `/api/accounts` | Kullanıcının hesaplarını listeler | ✅ |
| POST | `/api/accounts` | Yeni hesap oluşturur | ✅ |
| GET | `/api/accounts/{id}` | Hesap detayını getirir | ✅ |

#### `POST /api/accounts`

```json
{
  "name": "Vadesiz TL",
  "currency": "TRY",
  "initial_balance": 1000
}
```

**Kurallar:**
- `currency`: `TRY`, `USD` veya `EUR` olmalıdır
- `initial_balance`: 0'dan büyük veya eşit olmalıdır

**Başarılı yanıt (201):**
```json
{
  "account_user_id": 1,
  "success": "true"
}
```

#### `GET /api/accounts/{id}`

Sadece kendi hesabınızın detayını görebilirsiniz. Başka bir kullanıcıya ait hesap → 403.

**Başarılı yanıt (200):**
```json
{
  "balance": 1000,
  "created_at": "2026-07-09",
  "currency": "TRY",
  "name": "Vadesiz TL",
  "user_id": 1
}
```

---

### Transfers (Transferler)

| Method | Endpoint | Açıklama | Auth |
|--------|----------|----------|------|
| POST | `/api/transfers` | Transfer veya deposit yapar | ✅ |

#### `POST /api/transfers`

**Transfer (hesaplar arası):**
```json
{
  "from_account": 1,
  "to_account": 2,
  "amount": 250
}
```

**Deposit (para yatırma — `to_account` boş):**
```json
{
  "from_account": 1,
  "to_account": "",
  "amount": 500
}
```

**Kurallar:**
- `amount` > 0 olmalıdır
- `from_account` oturum açmış kullanıcıya ait olmalıdır
- Transfer için `from_account` bakiyesi yeterli olmalıdır
- Aynı hesaba transfer yapılamaz (409)
- İşlem **atomik** olarak gerçekleşir (SQLite transaction)

**Başarılı yanıt (201) — Transfer:**
```json
{
  "receiver_balance": 1250.0,
  "sender_balance": 750.0,
  "success": "true"
}
```

**İşlem kayıtları:**
- Gönderen hesap için `transfer_out` kaydı oluşturulur
- Alıcı hesap için `transfer_in` kaydı oluşturulur

---

### Transactions (İşlem Geçmişi)

| Method | Endpoint | Açıklama | Auth |
|--------|----------|----------|------|
| GET | `/api/accounts/{id}/transactions` | İşlem geçmişini listeler | ✅ |

#### `GET /api/accounts/{id}/transactions`

**Query parametreleri (opsiyonel):**

| Parametre | Format | Açıklama |
|-----------|--------|----------|
| `start_date` | `YYYY-MM-DD` | Bu tarihten sonraki işlemler |
| `end_date` | `YYYY-MM-DD` | Bu tarihten önceki işlemler |

**Örnek:**
```
GET /api/accounts/1/transactions?start_date=2026-01-01&end_date=2026-12-31
```

**Başarılı yanıt (200):**
```json
[
  {
    "account_id": 1,
    "amount": 250.0,
    "counterparty_account_id": 2,
    "created_at": "2026-07-10 14:40:00",
    "type": "transfer_out"
  },
  {
    "account_id": 1,
    "amount": 500.0,
    "counterparty_account_id": null,
    "created_at": "2026-07-10 14:38:00",
    "type": "deposit"
  }
]
```

Sonuçlar tarihe göre **azalan (DESC)** sırada döner.

---

## 🗄 Veritabanı Şeması

```
┌──────────────┐       ┌──────────────────┐       ┌────────────────────┐
│    users     │       │    accounts      │       │   transactions     │
├──────────────┤       ├──────────────────┤       ├────────────────────┤
│ id (PK)      │──────▶│ id (PK)          │──────▶│ id (PK)            │
│ email (UQ)   │       │ user_id (FK)     │       │ account_id (FK)    │
│ password_hash│       │ name             │       │ type               │
│ created_at   │       │ currency         │       │ amount             │
└──────────────┘       │ balance          │       │ counterparty_acc_id│
                       │ created_at       │       │ created_at         │
                       └──────────────────┘       └────────────────────┘
```

**İlişkiler:**
- `accounts.user_id` → `users.id` (bir kullanıcının birden fazla hesabı olabilir)
- `transactions.account_id` → `accounts.id` (bir hesabın birden fazla işlemi olabilir)
- `transactions.counterparty_account_id` → transfer işlemlerinde karşı tarafın hesap ID'si (deposit için `NULL`)

---

## 🖥 Tarayıcı Test Paneli

Uygulama çalıştıktan sonra tarayıcınızda **http://127.0.0.1:5000** adresine gidin.

Test panelinde şu işlemleri yapabilirsiniz:

| Kart | İşlev |
|------|-------|
| 🔐 Kayıt Ol | E-posta ve şifre ile yeni kullanıcı kaydı |
| 🔑 Giriş Yap | Mevcut kullanıcı ile oturum açma |
| 🏦 Hesap Oluştur | TRY/USD/EUR cinsinden yeni banka hesabı |
| 📋 Hesapları Listele | Tüm hesapların bakiye bilgileriyle listelenmesi |
| 🔍 Hesap Detayı | Belirli bir hesabın detay bilgileri |
| 💸 Transfer / Deposit | Hesaplar arası para transferi veya para yatırma |
| 📊 İşlem Geçmişi | Tarih filtreli işlem sorgulama |

Panelin üst kısmındaki **oturum göstergesi** aktif oturum durumunu gösterir. Her API çağrısının yanıtı sayfanın altındaki **yanıt panelinde** syntax-highlighted JSON olarak görüntülenir.

---

## 🧪 Test Senaryoları

Aşağıdaki adımları sırayla izleyerek tüm fonksiyonları test edebilirsiniz:

### Senaryo 1: Tam Akış Testi

```
1. Kayıt Ol
   → Email: test@ornek.com, Şifre: guvenli_sifre_123
   → Beklenen: 201 Created

2. Giriş Yap
   → Aynı email ve şifre ile
   → Beklenen: 200 OK, oturum göstergesi yeşile döner

3. Hesap Oluştur (Hesap A)
   → Ad: "Vadesiz TL", Para Birimi: TRY, Bakiye: 5000
   → Beklenen: 201 Created

4. Hesap Oluştur (Hesap B)
   → Ad: "Dolar Hesabı", Para Birimi: USD, Bakiye: 1000
   → Beklenen: 201 Created

5. Hesapları Listele
   → Beklenen: 200 OK, 2 hesap listelenir

6. Hesap Detayı
   → Hesap ID: 1
   → Beklenen: 200 OK, hesap bilgileri görüntülenir

7. Para Yatır (Deposit)
   → Gönderen: 1, Alıcı: (boş), Tutar: 500
   → Beklenen: 201 Created, bakiye 5500'e çıkar

8. Transfer
   → Gönderen: 1, Alıcı: 2, Tutar: 1000
   → Beklenen: 201 Created, Hesap A: 4500, Hesap B: 2000

9. İşlem Geçmişi
   → Hesap ID: 1
   → Beklenen: 200 OK, deposit ve transfer_out kayıtları görünür
```

### Senaryo 2: Hata Durumları

```
- Aynı email ile tekrar kayıt → 409 Conflict
- Yanlış şifre ile giriş → 401 Unauthorized
- Login olmadan hesap oluşturma → 401 Unauthorized
- Yetersiz bakiye ile transfer → 400 Bad Request
- Başka kullanıcının hesap detayı → 403 Forbidden
- Negatif veya sıfır tutar ile transfer → 400 Bad Request
- Aynı hesaba transfer → 409 Conflict
```

---

## 📌 HTTP Durum Kodları

| Kod | Anlamı | Kullanıldığı Yer |
|-----|--------|------------------|
| 200 | OK | Başarılı GET/login işlemleri |
| 201 | Created | Kayıt, hesap oluşturma, transfer |
| 400 | Bad Request | Hatalı input, iş kuralı ihlali |
| 401 | Unauthorized | Login olmadan erişim |
| 403 | Forbidden | Başka kullanıcının kaynağına erişim |
| 404 | Not Found | Olmayan kaynak |
| 409 | Conflict | Aynı email ile kayıt, aynı hesaba transfer |
| 500 | Server Error | Veritabanı bağlantı hatası |
