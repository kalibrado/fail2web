from flask import jsonify, request
from . import api_blueprint
from utils import run_fail2ban_command, parse_jail_status, validate_ip, require_sudo
from datetime import datetime

@api_blueprint.route('/banned-ips', methods=['GET'])
def get_all_banned_ips():
    output, error = run_fail2ban_command(['status'])
    if error:
        return jsonify({'error': error}), 500

    all_banned = []
    import re
    if output:
        match = re.search(r'Jail list:\s*(.+)', output)
        if match:
            jail_names = [j.strip() for j in match.group(1).split(',')]
            for jail_name in jail_names:
                jail_output, _ = run_fail2ban_command(['status', jail_name])
                if jail_output:
                    jail_data = parse_jail_status(jail_output)
                    for ip in jail_data['banned_ips']:
                        all_banned.append({
                            'ip': ip,
                            'jail': jail_name,
                            'banned_at': datetime.now().isoformat(),
                            'attempts': jail_data['current_failed']
                        })
    return jsonify({'banned_ips': all_banned, 'total': len(all_banned)})


@api_blueprint.route('/unban', methods=['POST'])
@require_sudo
def unban_ip():
    data = request.get_json()
    if not data or 'ip' not in data or 'jail' not in data:
        return jsonify({'error': 'IP et jail requis'}), 400

    ip = data['ip']
    jail = data['jail']

    if not validate_ip(ip):
        return jsonify({'error': 'IP invalide'}), 400

    output, error = run_fail2ban_command(['set', jail, 'unbanip', ip])
    if error:
        return jsonify({'error': error}), 500

    return jsonify({'success': True, 'message': f'IP {ip} débannie de {jail}', 'timestamp': datetime.now().isoformat()})


@api_blueprint.route('/ban', methods=['POST'])
@require_sudo
def ban_ip():
    data = request.get_json()
    if not data or 'ip' not in data or 'jail' not in data:
        return jsonify({'error': 'IP et jail requis'}), 400

    ip = data['ip']
    jail = data['jail']

    if not validate_ip(ip):
        return jsonify({'error': 'IP invalide'}), 400

    output, error = run_fail2ban_command(['set', jail, 'banip', ip])
    if error:
        return jsonify({'error': error}), 500

    return jsonify({'success': True, 'message': f'IP {ip} bannie dans {jail}', 'timestamp': datetime.now().isoformat()})
