# İş Takip Sistemi

Bu proje, Teknopark bünyesinde yapılan yaz stajı kapsamında geliştirilmiş,
**web tabanlı bir iş takip sistemidir**.  
Uygulama, kullanıcıların sisteme giriş yaparak iş ve görev kayıtlarını
takip edebilmesini sağlamak amacıyla geliştirilmiştir.

---

## Özellikler

- Kullanıcı kayıt ve giriş sistemi
- Kullanıcı yetkilendirme ve oturum yönetimi
- İş / görev kayıtlarının listelenmesi
- Veritabanı üzerinden CRUD (Create, Read, Update, Delete) işlemleri
- Test odaklı geliştirme yaklaşımı

---

## Kullanılan Teknolojiler

- **Backend:** Python, Flask  
- **Veritabanı:** SQLite, SQLAlchemy  
- **Kimlik Doğrulama:** Flask-Login  
- **Test:** pytest, pytest-flask  
- **Sistem:** Linux (Ubuntu), Bash  
- **Versiyon Kontrol:** Git  

---

## Veritabanı

Bu projede **SQLite** veritabanı kullanılmıştır.

Repository içerisinde bulunan `app.db` dosyası:
- **Demo amaçlıdır**
- Gerçek kullanıcı verisi içermez
- Projenin klonlandıktan sonra **doğrudan çalıştırılabilmesi** için eklenmiştir

---

## Kurulum ve Çalıştırma

### Projeyi Klonla
-git clone https://github.com/hmyrsrnl/is_takip_programi.git
-cd is_takip_programi

### Sanal Ortam Oluştur
-python -m venv myenv
-source myenv/bin/activate

### Gerekli Paketleri Yükle
-pip install -r requirements.txt

### Uygulamayı Çalıştır
-python app.py

---

## Proje Amacı
-Flask ile web tabanlı uygulama geliştirme
-Veritabanı tasarımı ve ORM kullanımı
-Kullanıcı kimlik doğrulama ve yetkilendirme
-Test yazma ve teknik dokümantasyon

---




