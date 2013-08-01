import re
from gettext import gettext as _
from jsonschema import Draft4Validator


template_search = re.compile(r'{{[\s]?([\w]+)[\s]?}}')
template_replacement = '({{[\s]?%s[\s]?}})'


def _replace_vars(root, message):
    """
    Replace placeholders in a JSON-schema message in the {{var}} form
    with their values found in the JSON-schema definition.
    """
    while template_search.search(message):
        name = template_search.search(message).groups()[0]
        message = re.sub(template_replacement %
                         name, root.get(name, "this"), message)
    return message.capitalize()


def get_error_dictionary(schema, instance):
    """
    Start with jsonschema and instance to test against, and return
    a dictionary with field names as keys and error messages as values,
    to be used directly by the front-end.
    """

    v = Draft4Validator(schema)
    errors = v.iter_errors(instance)
    d = {}

    # iterate through the validation errors
    for error in errors:
        root = error.schema
        # todo: add $ref handling
        if error.schema_path[0] == 'properties':
            # traverse the tree
            for i in range(1, len(error.schema_path) - 1):
                root = root.get(error.schema_path[i], root)

            # read the error messages
            if "errors" in root:
                message = root.get("errors", {}).get(error.schema_path[-1])
                d[error.schema_path[1]] = _replace_vars(root, message)
            else:
                # should never happen
                d[error.schema_path[1]] = _("Error when validating")
        else:
            # special case when error is not on a specific property
            message = root.get("errors", {}).get(error.schema_path[0])
            try:
                d[error.schema_path[1]] = _replace_vars(root, message)
            except IndexError:
                d[error.schema_path[0]] = _replace_vars(root, message)

    return d
