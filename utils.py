import ipaddress
import subprocess
import logging
import os
import json
import re
from flask import request
from config import SUPPORTED_LANGS, TRANSLATIONS_DIR
from functools import wraps

logger = logging.getLogger(__name__)

def validate_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def require_sudo(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


def create_jail_config(name, settings):
    conf_path = os.path.join(PATH_JAILS_DIR, f"{name}.conf")
    try:
        config_lines = [f"[{name}]"]
        for key, value in settings.items():
            config_lines.append(f"{key} = {value}")
        config_lines.append("")
        content = "\n".join(config_lines)
        result = subprocess.run(
            ["sudo", "bash", "-c", f"echo '{content}' > '{conf_path}'"],
           capture_output=True, text=True, timeout=10)
        print(result)
        logger.info(f"Jail config '{name}' created at {conf_path}")
    except Exception as e:
        logger.error(f"Erreur lors de la création du fichier de configuration de la jail '{name}': {e}")

def run_fail2ban_command(command):
    try:
        cmd = ['sudo', 'fail2ban-client'] + command
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            logger.error(f"Erreur fail2ban: {result.stderr}")
            return None, result.stderr
        return result.stdout.strip(), None
    except subprocess.TimeoutExpired:
        return None, "Timeout"
    except Exception as e:
        return None, str(e)

def parse_jail_status(output):
    data = {
        'filter': {},
        'actions': {},
        'total_banned': 0,
        'current_banned': 0,
        'total_failed': 0,
        'current_failed': 0,
        'banned_ips': []
    }

    lines = output.splitlines()
    for i, line in enumerate(lines):
        line = line.strip()

        if 'Currently banned:' in line:
            match = re.search(r'Currently banned:\s*(\d+)', line)
            if match:
                data['current_banned'] = int(match.group(1))

        elif 'Total banned:' in line:
            match = re.search(r'Total banned:\s*(\d+)', line)
            if match:
                data['total_banned'] = int(match.group(1))

        elif 'Currently failed:' in line:
            match = re.search(r'Currently failed:\s*(\d+)', line)
            if match:
                data['current_failed'] = int(match.group(1))

        elif 'Total failed:' in line:
            match = re.search(r'Total failed:\s*(\d+)', line)
            if match:
                data['total_failed'] = int(match.group(1))

        elif 'Banned IP list:' in line:
            after_colon = line.split(':', 1)[1].strip()
            ips = after_colon.split() if after_colon else []

            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if not next_line:
                    break
                if re.match(r'^[0-9a-fA-F:\.\s]+$', next_line):
                    ips.extend(next_line.split())
                    j += 1
                else:
                    break

            valid_ips = []
            for ip in ips:
                try:
                    ipaddress.ip_address(ip)
                    valid_ips.append(ip)
                except ValueError:
                    continue

            data['banned_ips'] = valid_ips

    return data

def get_user_lang():
    lang = request.cookies.get("lang")
    if not lang:
        lang = request.accept_languages.best_match(SUPPORTED_LANGS)
    if not lang or lang not in SUPPORTED_LANGS:
        lang = "en"
    return lang

def load_translations(lang):
    try:
        print(f"Chargement des traductions pour la langue: {lang}")
        path = os.path.join(TRANSLATIONS_DIR, f"{lang}.json")
        with open(path, "r", encoding="utf-8") as f:
            print(f"Chemin des traductions: {path}")
            return json.load(f)
    except Exception as e:
        logger.error(f"Impossible de charger les traductions pour {lang}: {e}")
        return {}
