from flask import jsonify, request
from . import api_blueprint
from utils import run_fail2ban_command, parse_jail_status
from datetime import datetime
import os
import json
import re

JAILS_JSON_DIR = "jail.d"

def read_jail_file(name):
    path = os.path.join(JAILS_JSON_DIR, f"{name}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)

def write_jail_file(name, data):
    os.makedirs(JAILS_JSON_DIR, exist_ok=True)
    with open(os.path.join(JAILS_JSON_DIR, f"{name}.json"), "w") as f:
        json.dump(data, f)

def get_enabled_status(name):
    data = read_jail_file(name)
    if data:
        return data.get("enabled", False)
    return False

@api_blueprint.route('/jails', methods=['GET'])
def get_jails():
    jails = {}
    
    # --- CLI Jails ---
    output, error = run_fail2ban_command(['status'])
    cli_jail_names = []
    if output:
        match = re.search(r'Jail list:\s*(.+)', output)
        if match:
            cli_jail_names = [j.strip() for j in match.group(1).split(',')]
    
    for jail_name in cli_jail_names:
        jail_output, jail_error = run_fail2ban_command(['status', jail_name])
        if jail_error:
            stats = {
                'banned': 0,
                'total_banned': 0,
                'failed': 0,
                'current_failed': 0,
                'banned_ips': []
            }
            status = 'inactive'
        else:
            stats = parse_jail_status(jail_output)
            status = 'active'
        # lire enabled depuis JSON si existe
        config = read_jail_file(jail_name) or {}
        jails[jail_name] = {
            'name': jail_name,
            'status': status,
            'enabled': config.get('enabled', True),
            **stats
        }
    
    # --- JSON only jails ---
    for root, dirs, files in os.walk(JAILS_JSON_DIR):
        for file in files:
            if file.endswith(".json"):
                name = file[:-5]
                if name not in jails:
                    data = read_jail_file(name)
                    if data:
                        jails[name] = {
                            'name': name,
                            'status': 'inactive',
                            'enabled': data.get('enabled', False),
                            'banned': 0,
                            'total_banned': 0,
                            'failed': 0,
                            'current_failed': 0,
                            'banned_ips': [],
                            **data
                        }

    return jsonify({'jails': list(jails.values())})

@api_blueprint.route('/jails/<jail_name>', methods=['GET'])
def get_jail_details(jail_name):
    output, error = run_fail2ban_command(['status', jail_name])
    if error:
        return jsonify({'error': error}), 404
    jail_data = parse_jail_status(output)
    jail_data['enabled'] = get_enabled_status(jail_name)
    return jsonify({
        'name': jail_name,
        'status': 'active',
        'data': jail_data,
        'timestamp': datetime.now().isoformat()
    })


@api_blueprint.route("/jails/add", methods=["POST"])
def add_jail():
    data = request.get_json()
    name = data.get("name")
    if not name:
        return jsonify({"error": "Nom de jail requis"}), 400

    try:
        run_fail2ban_command(["add", name])
        # Configuration optionnelle
        for key in ["filter", "addport", "maxretry", "bantime"]:
            if data.get(key):
                run_fail2ban_command(["set", name, key if key != "filter" else "addignoreip", str(data[key])])

        # Backup JSON
        data['enabled'] = True
        data['created_at'] = datetime.now().isoformat()
        data['path_log'] = f"/var/log/fail2ban/{name}.log"
        write_jail_file(name, data)

        return jsonify({"message": f"Jail '{name}' créée avec succès."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_blueprint.route('/jails/<jail_name>/toggle', methods=['PATCH'])
def toggle_jail(jail_name):
    config = read_jail_file(jail_name)
    if not config:
        return jsonify({"error": f"Jail '{jail_name}' non trouvée."}), 404

    try:
        if config.get("enabled", True):
            run_fail2ban_command(['stop', jail_name])
            config["enabled"] = False
            message = f"Jail '{jail_name}' désactivée."
        else:
            run_fail2ban_command(['add', jail_name])
            # réappliquer config
            for key in ["filter", "addport", "maxretry", "bantime"]:
                if config.get(key):
                    run_fail2ban_command(["set", jail_name, key if key != "filter" else "addignoreip", str(config[key])])
            config["enabled"] = True
            message = f"Jail '{jail_name}' activée."

        write_jail_file(jail_name, config)
        return jsonify({"message": message})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
