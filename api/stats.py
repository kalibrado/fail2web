from flask import jsonify
from . import api_blueprint
from utils import run_fail2ban_command
import subprocess
import re
from datetime import datetime, timedelta
from config import dashboard_version

def get_fail2ban_version():
    """Retourne la version de fail2ban."""
    output, error = run_fail2ban_command(['--version'])
    if error:
        return "Unknown"
    match = re.search(r'Fail2Ban v([\d\.]+)', output)
    if match:
        return match.group(1)
    return "Unknown"

def get_fail2ban_uptime():
    """Retourne le temps de vie de fail2ban à partir de ps (compatible conteneur)."""
    try:
        output = subprocess.check_output(
            ["ps", "-eo", "pid,comm,lstart,etime,time,args"],
            text=True
        )

        for line in output.splitlines():
            if "fail2ban-server" in line and "grep" not in line:
                # Exemple de ligne:
                # 11596 fail2ban-server Thu Oct 30 10:12:57 2025    03:12:02 00:00:08 /usr/bin/python3 /usr/bin/fail2ban-server ...
                parts = line.split(None, 7)  # coupe la ligne en 8 morceaux max
                if len(parts) < 8:
                    continue

                pid = parts[0]
                command = parts[1]
                start_str = " ".join(parts[2:7])  # Thu Oct 30 10:12:57 2025
                etime = parts[7].split()[0] if len(parts) >= 8 else None

                # Parse de la date de démarrage
                start_time = datetime.strptime(start_str, "%a %b %d %H:%M:%S %Y")

                # Calcul du uptime à partir de etime (format [DD-]HH:MM:SS)
                match = re.match(r"(?:(\d+)-)?(\d+):(\d+):(\d+)", etime)
                if match:
                    days, hours, minutes, seconds = match.groups(default="0")
                    uptime = timedelta(
                        days=int(days),
                        hours=int(hours),
                        minutes=int(minutes),
                        seconds=int(seconds)
                    )
                else:
                    uptime = timedelta(0)

                return {
                    "pid": pid,
                    "command": command,
                    "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "uptime_seconds": int(uptime.total_seconds()),
                    "uptime_human": str(uptime)
                }

        return {"error": "fail2ban-server not found"}

    except subprocess.CalledProcessError as e:
        return {"error": f"ps failed: {e}"}
    except Exception as e:
        return {"error": str(e)}

@api_blueprint.route('/stats', methods=['GET'])
def get_stats():
    output, error = run_fail2ban_command(['status'])
    if error:
        return jsonify({'error': error}), 500

    total_banned = 0
    total_failed = 0
    active_jails = 0

    if output:
        import re
        match = re.search(r'Jail list:\s*(.+)', output)
        if match:
            jail_names = [j.strip() for j in match.group(1).split(',')]
            active_jails = len(jail_names)
            for jail_name in jail_names:
                jail_output, _ = run_fail2ban_command(['status', jail_name])
                from utils import parse_jail_status
                if jail_output:
                    jail_data = parse_jail_status(jail_output)
                    total_banned += jail_data['current_banned']
                    total_failed += jail_data['total_failed']
    uptime = get_fail2ban_uptime().get("uptime_human", "N/A")


    return jsonify({
        'total_banned': total_banned,
        'active_jails': active_jails,
        'total_failed': total_failed,
        'today_bans': total_banned,
        'uptime': uptime,
        'timestamp': datetime.now().isoformat(),
        'fail2ban_version': get_fail2ban_version(),
         'dashboard_version': dashboard_version
    })


@api_blueprint.route('/health', methods=['GET'])
def health_check():
    output, error = run_fail2ban_command(['ping'])
    return jsonify({
        'api': 'ok',
        'fail2ban': 'ok' if not error and 'pong' in output.lower() else 'error',
        'timestamp': datetime.now().isoformat()
    })
