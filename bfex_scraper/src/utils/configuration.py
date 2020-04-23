import os
import json

from bfex_scraper import configuration


def get_attribute(attribute_name, fail_if_not_found=True, accepts=None, is_json=False):
    """Get credentials attribute required in the project. First
    check the environment variables, then the logging.py file"""

    if os.environ.get(attribute_name) is None:
        print(f'{attribute_name} is not specified as an environment variable')
        if hasattr(configuration, attribute_name):
            print(f'Retrieving {attribute_name} from configuration file')
            attribute = getattr(configuration, attribute_name)
            if attribute_name in['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']:
                os.environ[attribute_name] = attribute
            return attribute
        else:
            if fail_if_not_found:
                raise AttributeError(f'Cannot get {attribute_name} from environment or configuration file')
            else:
                print(f'Cannot get {attribute_name} from the environment or '
                      f'configuration file, returning None')
                return None
    else:
        attribute = os.environ.get(attribute_name)
        # Convert true/false arguments to booleans
        if attribute.lower() == 'true':
            attribute = True
        elif attribute.lower() == 'false':
            attribute = False
        if accepts is not None:
            if attribute in accepts:
                return attribute
            else:
                raise Exception(f'{attribute_name} only accepts the following: {str(accepts)}')
        else:
            if is_json:
                print(f'Loading {attribute_name} (JSON) from environment. Value: {attribute}')
                return json.loads(str(attribute))
            else:
                return attribute
