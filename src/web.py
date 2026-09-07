import subprocess
import pathlib


if __name__ == '__main__':
    from config import HTTP_HOST, HTTP_PORT

    cert_path = pathlib.Path(__file__).parent.parent / 'ssl' / 'tc.crt'
    key_path = pathlib.Path(__file__).parent.parent / 'ssl' / 'tc.key'

    # Gunicorn con SSL nativo
    subprocess.run([
        'gunicorn',
        '--bind', f'{HTTP_HOST}:{HTTP_PORT}',
        '--certfile', str(cert_path),
        '--keyfile', str(key_path),
        '--workers', '1',
        '--threads', '4',
        '--timeout', '60',
        'core.wsgi:application'
    ])