# sbf-tools
Tools zum Sportbootführerschein, oder *wie parse ich ELWIS*.

# Installation

Optional: Install most packages from repos (on archlinux):

```bash
sudo pacman -S python python-{pip,tornado,mimeparse}
```

Install `hug`:

```bash
pip3 install --user hug
```

# Usage

Check the script before running it. No guarantees - see license!

```bash
DATA="<your-data-dir>"
python3 crawler/crawl.py -o "$DATA" -d 
./run.sh "$DATA"

# License

GPLv3, see file `LICENSE`.

Auszug aus den Nutzungsbedingungen von [ELWIS](https://elwis.de):

> Copyright:
> Die Inhalte dieser Internetpräsentation dienen ausschließlich zur individuellen Information des Nutzers und dürfen nicht zu Zwecken der Wahlwerbung verwendet werden. Wiedergabe und Weitergabe von Inhalten dieser Internetpräsentation und Verweise darauf sind unentgeltlich und unter der Voraussetzung gestattet, dass sowohl die Quelle als auch die Internet-Adresse genannt werden.
