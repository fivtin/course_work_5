from configparser import ConfigParser


def config(filename="database.ini", section="postgresql"):
    parser = ConfigParser()

    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        db = dict(params)
    else:
        raise Exception(
            'Section {0} is not found in the {1} file.'.format(section, filename))
    return db
