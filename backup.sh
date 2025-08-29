#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups"
mkdir -p $BACKUP_DIR

cp app.db $BACKUP_DIR/app.db.backup
cp .env $BACKUP_DIR/.env.backup

tar -czf $BACKUP_DIR/backup_$DATE.tar.gz app.db .env
echo "Yedek oluşturuldu: $BACKUP_DIR/backup_$DATE.tar.gz"
find $BACKUP_DIR -name "*.tar.gz" -type f -mtime +30 -exec rm {} \;