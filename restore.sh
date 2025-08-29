#!/bin/bash

BACKUP_DIR="./yedekler"
if [ -z "$1" ]; then
    echo "Kullanım: ./restore.sh <yedek_dosyası>"
    echo "Örnek: ./restore.sh ./yedekler/full_backup_20231215_123045.tar.gz"
    exit 1
fi

BACKUP_FILE=$1

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Yedek dosyası bulunamadı: $BACKUP_FILE"
    exit 1
fi

echo "Yedek dosyası açılıyor: $BACKUP_FILE"
tar -xzf "$BACKUP_FILE" -C /tmp

BACKUP_BASENAME=$(basename "$BACKUP_FILE" .tar.gz)
BACKUP_DATE=${BACKUP_BASENAME#full_backup_}

echo "Veritabanı geri yükleniyor..."
sqlite3 instance/taskmanager.db < "/tmp/db_backup_$BACKUP_DATE.sql"

echo "Yapılandırma dosyası geri yükleniyor..."
cp "/tmp/env_backup_$BACKUP_DATE" .env

echo "Geçici dosyalar temizleniyor..."
rm -f "/tmp/db_backup_$BACKUP_DATE.sql" "/tmp/env_backup_$BACKUP_DATE"

echo "Geri yükleme işlemi tamamlandı: $BACKUP_FILE"