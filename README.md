# IL-2 Tank Crew Stats — Django 5.2 LTS Edition

Statistics system for a dedicated **IL-2 Sturmovik** server (Great Battles series,
with full **Tank Crew** support). It parses the server's mission text logs and
produces web-based statistics: player rankings, sorties, kill boards, tours,
squads, aircraft **and tank** stats, and more.

This repository is a **merged and modernized distribution** that combines:

- the original **IL-2 Stats** core (by the IL2 stats team), and
- the community **mod bundle** (Tank mod, Disconnect mod, Split Rankings /
  Stats Enhancements, and Global Aircraft Stats),

all **migrated from Django 1.11.29 to Django 5.2 LTS** and running on Python 3.11+.

> The mods are no longer a separate overlay you copy on top of a clean install —
> they are integrated into the codebase as first-class Django apps
> (`mod_rating_by_type` and `mod_stats_by_aircraft`) and are enabled/disabled
> purely through `conf.ini`.

> 🐳 **Dockerized:** this distribution ships with a ready-to-use Docker setup
> (`Dockerfile` + `docker-compose.yml`). You can bring up the database, web
> server and log parser with a single `docker compose up` — no local Python,
> PostgreSQL or virtualenv required. See
> [Installation → Docker](#docker-recommended-any-os).

---

## Table of contents

- [Technology stack](#technology-stack)
- [What's included](#whats-included)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Docker (recommended, any OS)](#docker-recommended-any-os)
  - [Windows (scripted)](#windows-scripted)
  - [Manual installation (any OS)](#manual-installation-any-os)
- [Configuration (`conf.ini`)](#configuration-confini)
  - [Enabling the mods](#enabling-the-mods)
  - [Stats Enhancements modules](#stats-enhancements-modules)
  - [Disconnect mod](#disconnect-mod)
  - [Retroactive computation](#retroactive-computation)
- [Running](#running)
- [Updating / reprocessing](#updating--reprocessing)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [Migration notes (1.11 → 5.2)](#migration-notes-111--52)
- [Credits](#credits)
- [License](#license)

---

## Technology stack

| Component        | Version                                    |
|------------------|--------------------------------------------|
| Django           | 5.2.x LTS (supported until April 2028)     |
| Python           | 3.11+ (3.12 recommended)                   |
| Database         | PostgreSQL 10+ (13+ recommended)           |
| Static files     | WhiteNoise                                 |
| App server       | Waitress                                   |
| Translations     | django-modeltranslation + django-rosetta   |
| Containerization | Docker + Docker Compose (optional)         |

> **Important:** IL-2 Stats collects statistics with its own algorithms, which
> differ from the in-game statistics. As a consequence, these numbers will not
> match the game exactly. The kill-count system is designed for a server running
> with the `finishMissionIfLanded` setting.

---

## What's included

- **Core stats** — sorties, tours, missions, players, squads, kill boards,
  rankings, awards, translations (EN/RU and more).
- **Tank mod** — tank missions, tank crews and tank-specific stats.
- **Disconnect mod** — extra handling for disconnection situations
  (early disco, damaged disco).
- **Stats Enhancements** (`mod_rating_by_type`) — a set of optional, individually
  switchable modules (split rankings, ammo breakdown, ironman modes, flight-time
  bonus, adjustable bonuses/penalties, gunner stats, rams, and more).
- **Global Aircraft Stats** (`mod_stats_by_aircraft`) — per-aircraft global stats
  with retroactive computation of historical tours.

---

## Requirements

> 🐳 Using **Docker**? Skip this whole section — the containers bundle Python and
> PostgreSQL, and the required extensions are created automatically. Jump to
> [Installation → Docker](#docker-recommended-any-os). You only need
> mission-text logging enabled on the game server (see the last step below).

Before installing **without Docker**, make sure you have:

1. **Python 3.11 or 3.12**
2. **PostgreSQL 10.0 or newer**
3. `pip` and `venv`
4. At least 1 GB of free disk space

Create the database and enable the required extensions:

```sql
CREATE EXTENSION IF NOT EXISTS hstore;
CREATE EXTENSION IF NOT EXISTS citext;
```

Enable mission text logging on the game server (in `startup.cfg`, `[KEY = system]`):

```
mission_text_log = 1
text_log_folder = "logs\txt\"
```

---

## Installation

### Docker (recommended, any OS)

The repository ships with a full Docker setup that runs the whole stack in
containers — **you don't need Python, PostgreSQL or a virtualenv on the host**,
only Docker.

| File                        | Purpose                                                        |
|-----------------------------|----------------------------------------------------------------|
| `Dockerfile`                | Application image (Python 3.12 + dependencies + source).       |
| `docker-compose.yml`        | Services: `db` (PostgreSQL), `web` (Waitress), `parser`.       |
| `docker/entrypoint.sh`      | Waits for the DB, runs migrations, `collectstatic`, CSV import, optional superuser. |
| `docker/conf.ini`           | Container application config (DB host = `db`, binds `0.0.0.0`).|
| `docker/postgres-init.sql`  | Creates the required `hstore` / `citext` extensions.           |
| `.env.example`              | Template for environment variables.                            |

#### Prerequisites

- **Docker Engine 20.10+** and **Docker Compose v2** (`docker compose ...`).
- That's it — no local Python or PostgreSQL needed.

#### 1. Configure the environment

Copy the template and edit it:

```bash
cp .env.example .env
```

`.env` variables:

| Variable                    | Meaning                                                            |
|-----------------------------|--------------------------------------------------------------------|
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` | PostgreSQL database name and credentials.                |
| `HTTP_PORT`                 | Host port the site is published on (container listens on `8077`).   |
| `SECRET_KEY`                | Stable Django secret key so sessions survive restarts. Generate one with `python -c "import secrets; print(secrets.token_urlsafe(50))"`. |
| `DJANGO_SUPERUSER_USERNAME` / `DJANGO_SUPERUSER_PASSWORD` / `DJANGO_SUPERUSER_EMAIL` | Auto-create an admin user on first start (leave blank to skip). |
| `IL2_SERVER_PATH`           | Path to your IL-2 dedicated server folder (the one containing `data/`). Used only by the parser. |

Application-level settings (mods, scoring, stats options) live in
**`docker/conf.ini`** — it already points the database at the `db` service and
binds the web server to `0.0.0.0`. Edit that file the same way you would edit
`src/conf.ini`, then rebuild.

#### 2. Start the web + database

```bash
docker compose up -d --build
```

The entrypoint automatically applies migrations, collects static files, imports
the game-object CSVs and (if configured) creates the admin user. The site is
then available at <http://localhost:8077> (or your `HTTP_PORT`); the admin panel
is at `/admin/`.

#### 3. Collect statistics (mission-log parser)

The `web` service only **displays** data; the **`parser`** service is what reads
your server's mission logs and fills the database. Point `IL2_SERVER_PATH` in
`.env` at your IL-2 dedicated server folder, then start the parser profile:

```bash
docker compose --profile parser up -d
```

The parser runs in a loop: every new mission your server writes is processed
automatically and shows up on the site.

> ⚠️ The server folder is mounted **read-write** on purpose — the parser moves
> processed logs into `data/<text_log_folder>/mission_report_backup/`.

> ℹ️ **Empty pilot ranking?** Two things are normal, not bugs:
> 1. The site defaults to the most recent **tour** — pick the right one in the
>    top selector (or `?tour=<id>`).
> 2. `inactive_player_days` hides pilots with no recent activity, so **old test
>    logs** won't appear in the ranking. With a live server producing fresh logs,
>    pilots show up automatically.

#### Data persistence

All state lives in **named Docker volumes**, independent of the containers:

| Volume                | Contents                                             |
|-----------------------|------------------------------------------------------|
| `il2_stats_pgdata`    | The entire PostgreSQL database.                      |
| `il2_stats_static`    | Collected static files.                              |
| `il2_stats_media`     | Uploaded media.                                      |

Removing or rebuilding containers does **not** touch these volumes:

| Command                          | Containers | Data (volumes)     |
|----------------------------------|------------|--------------------|
| `docker compose stop` / `down`   | removed    | ✅ kept             |
| `docker compose up --build`      | recreated  | ✅ kept             |
| `docker compose down -v`         | removed    | ❌ **deleted**      |

Only `down -v` (or deleting a volume manually) destroys the database.

Back up / restore the database:

```bash
docker compose exec db pg_dump -U il2_stats il2_stats > backup.sql        # backup
docker compose exec -T db psql -U il2_stats il2_stats < backup.sql        # restore
```

#### Common commands

```bash
docker compose logs -f web              # follow web logs
docker compose logs -f parser           # follow parser (log processing)
docker compose ps                       # container status
docker compose up -d --build            # apply code/config/conf.ini changes
docker compose down                      # stop (keeps data)
docker compose --profile parser down    # stop including the parser
```

### Windows (scripted)

1. Open a **clean shell** (system Python — *not* an already-activated virtualenv).
2. Configure `src/conf.ini` (see [Configuration](#configuration-confini)).
3. From the project root, run:

   ```
   run\install.cmd
   ```

   This will:
   - create the virtual environment and install dependencies,
   - run database migrations,
   - collect static files,
   - import game-object data (`objects.csv`, `score.csv`, `classes.csv`),
   - prompt you to create an admin user (admin panel: `http://<host>/admin/`).

> ⚠️ **Never run `install.cmd` / `update.cmd` from inside the project's own
> `.venv`.** The script recreates the virtualenv, and Windows cannot overwrite a
> `python.exe` that is currently in use — this corrupts `.venv` (you'll see
> `No pyvenv.cfg file`). Always run it from a fresh terminal.

### Manual installation (any OS)

```bash
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd src
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py import_csv_data
python manage.py createsuperuser
```

---

## Configuration (`conf.ini`)

All configuration lives in `src/conf.ini`. Key sections:

```ini
[http]
host = 127.0.0.1
port = 8077

[database]
host = 127.0.0.1
port = 5432
name = il2_stats
user = il2_stats
password = il2_stats

[game_server]
path = C:\path\to\your\game_server

[stats]
mission_report_delete = false
mission_report_backup_days = 31
inactive_player_days = 7
new_tour_by_month = true
win_by_score = true
win_score_min = 2000
win_score_ratio = 1.25
sortie_min_time = 0
```

Common `[stats]` keys:

| Key                          | Meaning                                                                 |
|------------------------------|-------------------------------------------------------------------------|
| `mission_report_delete`      | Delete already-processed logs (`true`/`false`).                         |
| `mission_report_backup_days` | Days to keep zipped backups of processed logs.                         |
| `inactive_player_days`       | Days of inactivity before a player drops out of the rankings.          |
| `new_tour_by_month`          | Automatically open a new tour each calendar month (`true`/`false`).    |
| `win_by_score`               | Decide mission victory by score when there is no task-based victory.   |
| `win_score_min`              | Minimum score for a coalition to win on score.                         |
| `win_score_ratio`            | Minimum score ratio between coalitions to determine the winner.        |

### Enabling the mods

Both mod apps are activated with the `mods` key under `[stats]`:

```ini
[stats]
mods = mod_rating_by_type, mod_stats_by_aircraft
```

### Stats Enhancements modules

`mod_rating_by_type` exposes individually switchable modules via `modules`:

```ini
[stats]
modules = split_rankings, ammo_breakdown, ironman_stats, last_mission_ironman,
          ironman_squad, flight_time_bonus, adjustable_bonuses_penalties,
          top_last_mission, rearm_accuracy_workaround, bailout_accuracy_workaround,
          gunner_stats, rams
```

Available module flags:

`split_rankings`, `ammo_breakdown`, `ironman_stats`, `last_mission_ironman`,
`ironman_squad`, `undamaged_bailout_penalty`, `flight_time_bonus`,
`adjustable_bonuses_penalties`, `top_last_mission`, `rearm_accuracy_workaround`,
`bailout_accuracy_workaround`, `mission_win_new_tour`, `air_streaks_no_ai`,
`gunner_stats`, `rams`, `itaf_layout`, `no_parachute_deaths`.

> ⚠️ **`mission_win_new_tour`** starts a brand-new tour after **every** won
> mission. This overrides `new_tour_by_month` and can create a very large number
> of tours. Enable it only if that is exactly the tour model you want; otherwise
> leave it out to keep the standard "one tour per month" behaviour.

`ironman_style` (`classic` / `both`, default `classic`) is a separate optional key.

If you enable **Adjustable Bonuses and Penalties**, tank-specific bonus/penalty
values can be tuned in the admin panel under **Scoring**:

| Config name              | Default |
|--------------------------|---------|
| `tank_bonus_landed`      | 100%    |
| `tank_bonus_winning_coa` | 25%     |
| `tank_bonus_in_flight`   | 100%    |
| `tank_bonus_in_service`  | 100%    |
| `tank_penalty_dead`      | 75%     |
| `tank_penalty_captured`  | 75%     |
| `tank_penalty_bailout`   | 50%     |
| `tank_penalty_shotdown`  | 20%     |

### Disconnect mod

Configure under `[stats]` (values in seconds):

```ini
[stats]
sortie_disco_min_time = 0
sortie_damage_disco_time = 120
```

### Retroactive computation

For Global Aircraft Stats and Split Rankings, choose how many past tours to
compute retroactively:

```ini
[stats]
retro_compute_for_last_tours = 10
```

- `-1` — disable retroactive computation
- `0` — compute for all sorties in the current tour
- `N` — compute for the last `N` tours

---

## Running

### Docker

- `docker compose up -d` — start the web server (and database).
- `docker compose --profile parser up -d` — additionally start the mission-log
  parser. See [Installation → Docker](#docker-recommended-any-os).

### Windows

- `run\stats.cmd` — start the mission-log parser (processes reports, then waits
  for new ones).
- `run\waitress.cmd` — start the built-in web server.

The web interface is available at the host/port configured in `[http]`
(default: `http://127.0.0.1:8077`).

### Linux/Mac

- `run/stats.sh` — start the parser.
- `run/waitress.sh` — start the web server.

The server name shown on the site is changed in the admin panel under **Chunks**.

---

## Updating / reprocessing

To update the codebase and dependencies, run `run\update.cmd`
(Windows) / `run/update.sh` (Linux/Mac) from a **clean shell**.

> 🐳 **With Docker**, update by rebuilding the image: `docker compose up -d --build`
> (migrations run automatically on start).

Some changes (new game objects, turret→aircraft mappings, or scoring logic)
only affect **newly processed** reports. To re-apply them to already-processed
missions, do a clean reprocess (the raw server logs are re-parsed automatically):

```bash
cd src
python manage.py flush --noinput          # wipes all data (also users!)
python manage.py import_csv_data          # re-populate game objects/scores
python manage.py createsuperuser          # recreate the admin user
# then run stats.cmd to reprocess the reports
```

> 🐳 **With Docker**, the same reprocess is:
> ```bash
> docker compose exec web python manage.py flush --noinput
> docker compose exec web python manage.py import_csv_data
> docker compose exec web python manage.py createsuperuser
> docker compose --profile parser restart parser   # reprocess the reports
> ```

---

## Customization

- **Scores** are edited in the admin panel (`/admin/`), section **Scoring**.
- **Templates and CSS**: copy the file (and subdirectories, if needed) into the
  `custom` directory. Files under `custom` take precedence over the originals,
  which keeps upgrades clean. Run `collectstatic` after changing CSS, images or
  templates.
- **Email** (registration activation / password reset) is configured in the
  `email` section. It is disabled by default; the features that depend on it are
  automatically deactivated when disabled.

---

## Troubleshooting

- **`No pyvenv.cfg file`** — the virtualenv was corrupted, typically by running
  `install.cmd`/`update.cmd` from inside the active `.venv`. Delete `.venv` and
  re-run the script from a clean shell.
- **`relation "tours" does not exist`** on a fresh database — this was a bug in
  the mods' background jobs querying the DB during app startup; it is fixed in
  this distribution. If you see it, make sure you are running this merged version
  and have applied migrations.
- **A flood of tours** — `mission_win_new_tour` is enabled. Remove it from
  `modules` (see the warning above) and reprocess.
- **`Could not find aircraft for turret ...`** — harmless warning for AI-only
  aircraft (e.g. B25/B26 bombers). Known playable turrets (e.g. Me 410) are
  mapped correctly in this distribution.
- Application logs are written to `django.log` / `stats.log` in the project root.

---

## Migration notes (1.11 → 5.2)

This distribution carries the full Django 1.11 → 5.2 LTS migration, including:

- URL routing migrated from deprecated `url()` to `path()` / `re_path()`.
- Deprecated translation APIs (`ugettext_lazy` → `gettext_lazy`).
- PostgreSQL `JSONField` moved from `django.contrib.postgres.fields` to
  `django.db.models.JSONField` (including historical migrations).
- `{% load staticfiles %}` → `{% load static %}` in templates.
- `tzlocal` 5.x API change (`get_localzone().zone` → `str(get_localzone())`).
- Modernized dependencies (psycopg2-binary, Pillow, WhiteNoise, numpy/scipy/
  scikit-learn for the ammo-breakdown mod, etc.).
- Fixes to mod code exposed by the newer stack (DB access during `ready()`,
  `Tour.save()` ordering, `sorties_cls` KeyError for tank turrets).

See `MIGRATION_REPORT.md` for the full technical report, and the Django 5.2
documentation at <https://docs.djangoproject.com/en/5.2/>.

---

## Credits

This project would not exist without the work of the original authors and the
modding community:

- **IL-2 Stats core** — the IL2 stats team, **=FB=Vaal** and **=FB=Isay**.
- **Tank mod** and **Disconnect mod** — **CountZero**.
- **Split Rankings / Stats Enhancements** and **Global Aircraft Stats** —
  **=FEW=Revolves** and **Enigma89**.
- **Mod bundle compilation** — **=FEW=Revolves**.
- **Django 5.2 LTS migration & merge** — this repository's maintainers.

Original mod threads on the IL-2 forums:

- Tank mod: <https://forum.il2sturmovik.com/topic/55657-mod-to-add-tank-missions-for-il2-stats-system-made-by-fbvaal-and-fbisay/>
- Disconnect mod: <https://forum.il2sturmovik.com/topic/56709-mod-for-il2-stats-system-more-options-for-disconnection-situations/>
- Split Rankings: <https://forum.il2sturmovik.com/topic/69965-il-2-stats-submod-split-rankings/>
- Global Aircraft Stats: <https://forum.il2sturmovik.com/topic/70380-il-2-stats-mod-global-aircraft-stats/>
- IL-2 Stats: <https://forum.il2sturmovik.com/topic/19083-il2-stats-statistics-system-for-a-dedicated-server-il2-battle-of-stalingrad/>

---

## License

Released under the **MIT License**. All original IL-2 Stats code and the merged
mods retain their MIT licensing. See [`LICENSE.txt`](LICENSE.txt) for the full
text and the list of copyright holders.
