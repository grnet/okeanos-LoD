import argparse

from subprocess import call


class AdminMessageManager:

    def __init__(self):
        pass

    HTML = "<section class=\"content\">\n" \
           "  <div class=\"row\">\n" \
           "    <div class=\"col-xs-12\">\n" \
           "      <!-- Choose class from alert-success | alert-info | alert-warning | alert-danger -->\n" \
           "      <div class=\"alert {alert_class}\">\n" \
           "        <!-- Choose icon from fa-check | fa-info | fa-warning | fa-close -->\n" \
           "        <h4 id=\"title\"><i class=\"icon fa {icon_class}\"></i>{title}</h4>\n" \
           "        <p id=\"message\">{message}</p>\n" \
           "      </div> <!-- class -->\n" \
           "    </div> <!-- col-xs-12 -->\n" \
           "  </div><!-- row -->\n" \
           "</section>"

    FILE_PATH = "app/templates/components/admin-message.hbs"

    BOOTSTRAP_CLASSES = {
        'alert': {
            'danger': "alert-danger",
            'warning': "alert-warning",
            'info': "alert-info",
            'success': "alert-success"
        },
        'icon': {
            'danger': "fa-ban",
            'warning': "fa-warning",
            'info': "fa-info",
            'success': "fa-check"
        }
    }

    def set(self, title=" Title", message="Message", type="info"):
        # Set the admin message file.
        print "Copying html file..."
        file_object = open(self.FILE_PATH, 'w')
        file_object.write(self.HTML.format(alert_class=self.BOOTSTRAP_CLASSES['alert'][type],
                                           icon_class=self.BOOTSTRAP_CLASSES['icon'][type],
                                           title=title, message=message))
        file_object.close()
        print "html file has been successfully copied!"

        # Build ember.
        print "Building Ember for production..."
        call(['ember build --environment=production'], shell=True)
        print "Ember for production has been successfully built!"

    def remove(self):
        self.set()


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description="Admin Message")

    argument_parser.add_argument('--action', type=str, dest='action', default='set',
                                 choices=['set', 'remove'],
                                 help="set or remove an admin message (default: set)")
    argument_parser.add_argument('--title', type=str, dest='title', default=" Title",
                                 help="title of the admin message"
                                      " (used only with set action, default:\" Title\")")
    argument_parser.add_argument('--message', type=str, dest='message', default="Message",
                                 help="admin message"
                                      " (used only with set action, default=\"Message\")")
    argument_parser.add_argument('--type', type=str, dest='type', default='info',
                                 choices=['danger', 'warning', 'info', 'success'],
                                 help="the type of the message"
                                      " (used only with set action, default=\"info\")")

    arguments = argument_parser.parse_args()

    admin_message_manager = AdminMessageManager()
    if arguments.action == 'remove':
        admin_message_manager.remove()
    elif arguments.action == 'set':
        admin_message_manager.set(type=arguments.type, title=arguments.title,
                                  message=arguments.message)
