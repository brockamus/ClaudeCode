#!/usr/bin/env bash
# Uploads site/ to proposals.konversly.com/jja-cleaning/ on Bluehost.
# Needs lftp and these env vars (from Bluehost cPanel > FTP Accounts):
#   KONVERSLY_FTP_HOST   e.g. ftp.konversly.com
#   KONVERSLY_FTP_USER
#   KONVERSLY_FTP_PASS
#   KONVERSLY_FTP_ROOT   remote folder that serves proposals.konversly.com
#                        (cPanel shows it as the subdomain's document root)
# Optional: KONVERSLY_FTP_VERIFY_CERT=no if the FTP cert is issued for the
#           Bluehost server name rather than your domain.
set -euo pipefail
cd "$(dirname "$0")/.."
: "${KONVERSLY_FTP_HOST:?set KONVERSLY_FTP_HOST}"
: "${KONVERSLY_FTP_USER:?set KONVERSLY_FTP_USER}"
: "${KONVERSLY_FTP_PASS:?set KONVERSLY_FTP_PASS}"
: "${KONVERSLY_FTP_ROOT:?set KONVERSLY_FTP_ROOT}"
TARGET="${KONVERSLY_FTP_ROOT%/}/jja-cleaning"

test -f site/index.html || { echo "run npm run build first" >&2; exit 1; }

lftp -u "$KONVERSLY_FTP_USER","$KONVERSLY_FTP_PASS" "ftp://$KONVERSLY_FTP_HOST" <<LFTP
set ftp:ssl-force true
set ssl:verify-certificate ${KONVERSLY_FTP_VERIFY_CERT:-yes}
mkdir -p $TARGET
mirror --reverse --delete --verbose site/ $TARGET/
bye
LFTP
echo "Deployed: http://proposals.konversly.com/jja-cleaning/"
