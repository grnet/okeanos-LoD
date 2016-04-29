from jinja2 import Environment, FileSystemLoader
import socket
import os
import yaml

if __name__ == '__main__':
    env = Environment(loader=FileSystemLoader('../ansible/roles/ember/templates'))
    template = env.get_template('environment.js.j2')
    ansible_hostname = socket.gethostname()

    variables_file = open("../ansible/roles/service-vm/vars/main.yml")
    max_upload_file_size = yaml.load_all(variables_file).next()['max_upload_file_size']

    settings = template.render(ansible_hostname=ansible_hostname,
                               max_upload_file_size=max_upload_file_size)
    if not os.path.exists('config'):
        os.mkdir('config')
    with open('config/environment.js', 'w') as f:
        f.write(settings)
