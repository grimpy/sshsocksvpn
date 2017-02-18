from configparser import ConfigParser
import os


class Config:
    def __init__(self, configpath):
        path = configpath
        if not os.path.exists(path):
            raise ValueError("Config file {} does not exists".format(path))
        try:
            config = ConfigParser()
            with open(path) as f:
                config.read_file(f)
        except Exception as e:
            raise ValueError("Failed to read config {}".format(e))

        self.servers = dict()
        self.config = config
        self.parse()

    def parse(self):
        def get_section_dict(section):
            options = dict()
            for option in self.config.options(section):
                options[option] = self.config.get(section, option)
            return options

        for section in self.config.sections():
            configtype, _, name = section.partition('.')
            if configtype == 'server':
                server = get_section_dict(section)
                if 'routes' in server:
                    server['routes'] = [route.strip() for route in server['routes'].split(',')]
                elif 'network' in server:
                    routes = []
                    server['routes'] = routes
                    for networkname in server['network'].split(','):
                        networkname = networkname.strip()
                        network = get_section_dict('network.{}'.format(networkname))
                        routes.extend([route.strip() for route in network['routes'].split(',')])
                self.servers[name] = server
