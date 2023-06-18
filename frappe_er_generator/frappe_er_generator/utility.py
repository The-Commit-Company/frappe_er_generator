import frappe
import os


@frappe.whitelist()
def get_whitelist_methods_in_app(app):
    # directory = frappe.get_app_path('emotive_app')
    directory = frappe.get_app_path(app)

    whitelisted_functions = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines):
                        if "@frappe.whitelist" in line and not is_commented(line):
                            function_name, params = get_function_name(lines, i)
                            whitelisted_functions.append(
                                {'function': function_name, 'params': params, 'file': file_path, 'line': i + 2})

    return whitelisted_functions


def get_function_name(lines, index):
    params = []
    for line in lines[index:]:
        if 'def' in line:
            data = ' '.join(line.split()[1:])
            params = data.split('(')[1].split(')')[0].split(',')
            params = [param for param in params if param != '']
            return data.split(':')[0], params

    return None


def is_commented(line):
    stripped_line = line.strip()
    if stripped_line.startswith('#'):
        return True
    elif '#' in stripped_line:
        return stripped_line.index('#') < stripped_line.index('@frappe.whitelist')
    else:
        return False
