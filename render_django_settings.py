from yaml import load
from jinja2 import Environment, FileSystemLoader

if __name__ == '__main__':
    env = Environment(loader=FileSystemLoader('webapp/ansible/roles/service-vm/templates'))
    template = env.get_template('settings.py.j2')
    with open("webapp/ansible/roles/service-vm/vars/main.yml", 'r') as stream:
        parsed = load(stream)
    settings = template.render(parsed)
    with open("webapp/webapp/settings.py", 'w') as f:
        f.write(settings)
