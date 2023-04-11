import frappe
from frappe.config import get_modules_from_app, get_modules_from_all_apps
import graphviz


def get_apps():
    return frappe.get_all_apps()


@frappe.whitelist()
def get_all_modules_from_all_apps():
    app_module_object = {}
    app_module = get_modules_from_all_apps()
    for i in app_module:
        if i.get('app') in app_module_object.keys():
            app_module_object[i.get('app')].append(i.get('module_name'))
        else:
            app_module_object[i.get('app')] = [i.get('module_name')]
    return app_module_object


@frappe.whitelist()
def get_doctype_from_app():
    doctype_list = []
    module = get_modules_from_app('emotive_app')
    for i in module:
        doctype_list.append(get_doctypes_from_module(i.module_name))
    return doctype_list


@frappe.whitelist()
def get_doctypes_from_module(module):
    return {'doctype': [doctype['name'] for doctype in frappe.get_list('DocType', filters={'module': module})], 'module': module}


@frappe.whitelist()
def get_doctype_json():
    # return frappe.get_doc('DocType', 'Lead').as_dict()
    return frappe.get_meta('Lead').as_dict()


"""
@params doctypes: list of doctypes
"""


@frappe.whitelist()
def get_erd(doctypes):
    # doctypes = get_doctypes_from_module('CRM')
    json_list = []
    fetch_from_list = []
    table_list = []
    connections_string_list = []
    fetch_from_string_list = []
    for doctype in doctypes['doctype']:
        data = frappe.get_meta(doctype).as_dict()
        json_list.append(data)
        fetch_from_list += [{**x, 'doctype': data.get('name')}
                            for x in data.get('fields') if x['fieldtype'] == 'Link']

    for doctype_data in json_list:
        table, connection_list, fetch_from = get_table(
            doctype_data, fetch_from_list, doctypes['doctype'])
        table_list.append(table)
        connections_string_list += connection_list
        fetch_from_string_list += fetch_from

    graph_string = get_graph_string(
        table_list, connections_string_list, fetch_from_string_list)

    create_graph(graph_string)

    return fetch_from_list


def create_graph(graph_string):
    graph = graphviz.Source(graph_string)
    graph.format = 'png'
    graph.render('erd', view=True)


def get_table(data, fetch_from_list, doctypes):
    table_element_list = []
    remove_fieldtype = ['Column Break', 'Section Break', 'Tab Break']
    connection_list = []
    fetch_from = []
    for field in data.get("fields"):
        if field.get('fieldtype') not in remove_fieldtype:
            table_element_list.append(
                f'<tr><td port="{field.get("fieldname")}">{field.get("label")}</td></tr>')
        if field.get("fieldtype") == "Link":
            connection_data = get_connection(field, data.get("name"), doctypes)
            if connection_data:
                connection_list.append(connection_data)
        if field.get("fetch_from") != None:
            fetch_data = get_fetch_from(field, data.get(
                "name"), fetch_from_list, doctypes)
            if fetch_data:
                fetch_from.append(fetch_data)

    table_elements = "\n".join(table_element_list)

    table = f"""{"".join(c if c.isalnum() else "_" for c in data.get("name")).lower()} [label=<
    <table border="0" cellborder="1" cellspacing="0">
    <tr><td port = "name"><b>{data.get("name")}</b></td></tr>
    {table_elements}
    </table>>];"""

    return table, connection_list, fetch_from


def get_connection(data, doctype_name, doctypes):
    if data.get("options") in doctypes:
        connection_string = f"""{"".join(c if c.isalnum() else "_" for c in doctype_name).lower()}:{data.get('fieldname')} -> {"".join(c if c.isalnum() else "_" for c in data.get("options")).lower()}:name;"""
        return connection_string

    return None


def get_fetch_from(data, doctype_name, fetch_from_list, doctypes):
    fetch_link_object = next(x for x in fetch_from_list if x.get(
        "fieldname") == data.get("fetch_from").split(".")[0])
    if fetch_link_object.get('options') in doctypes:
        fetch_string = f"""{"".join(c if c.isalnum() else "_" for c in fetch_link_object.get('doctype')).lower()}:{data.get('fieldname')} -> {"".join(c if c.isalnum() else "_" for c in fetch_link_object.get('options')).lower()}:{data.get("fetch_from").split(".")[1]} [style="dashed"];"""
        return fetch_string

    return None


def get_graph_string(table_list, connections_string_list, fetch_from_string_list):
    table_string = "\n\n".join(table_list)
    connections_string = "\n".join(connections_string_list)
    fetch_from_string = "\n".join(fetch_from_string_list)
    graph_string = f"""
        digraph {{
            graph [pad="0.5", nodesep="0.5", ranksep="2",legend="Fetch from\\l\\nNormal Link\\l"];
            node [shape=plain]
            rankdir=LR;

            {table_string}

        {connections_string}

        {fetch_from_string}

        subgraph cluster_01 {{ 
            label = "Legend";
            key [label=<<table border="0" cellpadding="2" cellspacing="0" cellborder="0">
            <tr><td align="left" port="i1">Link</td></tr>
            <tr><td align="left" port="i2">Fetch from</td></tr>
            </table>>]
            key2 [label=<<table border="0" cellpadding="2" cellspacing="0" cellborder="0">
            <tr><td port="i1">&nbsp;</td></tr>
            <tr><td port="i2">&nbsp;</td></tr>
            </table>>]
            key:i1:e -> key2:i1:w 
            key:i2:e -> key2:i2:w [style=dashed]
        }}
        }}
    """
    return graph_string
