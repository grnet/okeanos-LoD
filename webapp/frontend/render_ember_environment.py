from jinja2 import Environment, FileSystemLoader
import socket
import os

if __name__ == '__main__':
    env = Environment(loader=FileSystemLoader('../ansible/roles/ember/templates'))
    template = env.get_template('environment.js.j2')
    hostname = {'stdout_lines': socket.gethostname()}
    settings = template.render(hostname=hostname)
    if not os.path.exists('config'):
        os.mkdir('config')
    with open('config/environment.js', 'w') as f:
        f.write(settings)
