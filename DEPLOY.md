# BIO deploy notes (Portal tile 14)

Tile id 14, slug `bio-business-intelligence-officer`, **Live**, `mount_path=/bio`. Port **8504**.

Caddy: `handle_path /bio* { reverse_proxy 127.0.0.1:8504 }` with `BIO_STRIP_PREFIX=true`.

Cookie `portal_token_bio`, launch `/portal/launch/bio`, EdDSA PEM `PORTAL_SSO_PUBLIC_KEY`, never `keys=[]`.

See `deploy/com.tereo.bio.plist` and `deploy/portal-tile-bio.json`. Do not dest MMS.
