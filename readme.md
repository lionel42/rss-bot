# RSS → Mattermost Bot

Python script that reads RSS feeds and posts new items to a Mattermost channel via webhook. Can run continuously with systemd.

## Requirements
```
pip install feedparser requests
```

## Usage
```
python main.py https://example.com/rss https://another.com/feed --interval 600 --mattermost-url https://mattermost.example/hooks/your-webhook-id
```
- feeds → one or more RSS URLs
- --interval → check interval in seconds (default 300)
- --mattermost-url → Mattermost webhook URL

## systemd Setup
On linux, your can run the script as a service using systemd.

Copy the service file to `/etc/systemd/system/rss2mm.service`:

Edit it with your setup.

Enable & start:
```
sudo systemctl daemon-reload
sudo systemctl enable rss2mm
sudo systemctl start rss2mm
```

Check logs:
```
journalctl -u rss2mm -f
```
