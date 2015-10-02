from yaml import load
from jinja2 import Environment, FileSystemLoader

if __name__ == '__main__':
    env = Environment(loader=FileSystemLoader('ansible/roles/service-vm/templates'))
    template = env.get_template('settings.py.j2')
    with open("ansible/roles/service-vm/vars/main.yml", 'r') as stream:
        parsed = load(stream)
    settings = template.render(parsed)
    with open("webapp/settings.py", 'w') as f:
        f.write(settings)
