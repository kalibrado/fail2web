from flask import jsonify, request
from . import api_blueprint
from utils import run_fail2ban_command
from config import LOG_FILE
import subprocess

@api_blueprint.route('/logs', methods=['GET'])
def get_logs():
    try:
        lines = int(request.args.get('lines', 50))
        result = subprocess.run(['sudo', 'tail', '-n', str(lines), LOG_FILE], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return jsonify({'error': 'Impossible de lire les logs'}), 500
        logs = result.stdout.strip().split('\n')
        return jsonify({'logs': logs, 'count': len(logs)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
