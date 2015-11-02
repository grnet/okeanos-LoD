from jinja2 import Environment, FileSystemLoader
import socket
import os

if __name__ == '__main__':
    env = Environment(loader=FileSystemLoader('../ansible/roles/ember/templates'))
    template = env.get_template('environment.js.j2')
    ansible_hostname = socket.gethostname()
    settings = template.render(ansible_hostname=ansible_hostname)
    if not os.path.exists('config'):
        os.mkdir('config')
    with open('config/environment.js', 'w') as f:
        f.write(settings)
