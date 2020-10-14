from jsonify_html.cmd import CommandManager
from dateutil import parser as datetime_parser


def convert_type(type_name, obj):
    if type_name in ['str', 'int', 'bool']:
        return eval(f'{type_name}(obj)')
    elif type_name in ['datetime', 'date', 'time']:
        return datetime_parser.parse(obj).isoformat()
    elif type_name == 'list':
        if obj is None:
            return list()
        return obj if isinstance(obj, list) else list(obj)
    elif type_name == 'set':
        if obj is None:
            return list()
        return list(obj) if isinstance(obj, set) else list(set(obj))
    elif type_name == 'dict':
        if obj is None:
            return dict()
        return obj if isinstance(obj, dict) else dict(obj)
    else:
        return obj


def build_object(template, root):
    obj = dict()
    for key, content in template.items():
        content_type = content['$type']
        if content_type in ['object', 'obj']:
            obj[key] = dict()
            for obj_key, sub_template in content.items():
                if obj_key != '$type':
                    obj[key][obj_key] = parse_template(sub_template, root)
        else:
            result = CommandManager().run_commands(content['$cmd'], root)
            obj[key] = convert_type(content_type, result)
    return obj


def parse_template(template, root):
    if '$type' in template:
        return build_object({'$_plain': template}, root)['$_plain']
    else:
        return build_object(template, root)
