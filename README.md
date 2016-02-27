# sbf-tools
Tools zum Sportbootführerschein

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
