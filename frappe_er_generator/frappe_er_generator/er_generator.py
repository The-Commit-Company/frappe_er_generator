import frappe
from frappe.config import get_modules_from_app, get_modules_from_all_apps
import graphviz


def get_apps():
    # get all the apps installed on the bench
    return frappe.get_all_apps()


@frappe.whitelist()
def get_all_modules_from_all_apps():
    # get all the modules from all the apps installed on the bench
    app_module_object = {}
    app_module = get_modules_from_all_apps()
    for i in app_module:
        if i.get('app') in app_module_object.keys():
            app_module_object[i.get('app')].append(i.get('module_name'))
        else:
            app_module_object[i.get('app')] = [i.get('module_name')]
    return app_module_object


@frappe.whitelist()
def get_doctype_from_app(app):
    doctype_list = []
    module = get_modules_from_app(app)
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
@api {get} /api/method/frappe_er_generator.er_generator.get_erd Get ERD
@apiName get_erd
@apiQuery {String} doctypes Doctypes

@apiSuccess {String} message Success {Generate ERD with name erd.png}
"""


@frappe.whitelist()
def get_erd(doctypes, child_tables=True, amended_from=False):
    # 1. This is very generic function only have to pass list of doctypes
    # 2. This function will generate ERD for all the doctypes passed
    doctypes = set(doctypes)

    # json_list is list of doctype json data(meta data)
    json_list = []

    # link_list is the list of all `Link` fieldtype fields objects, because we need Link doctype name to generate connection in ERD.
    # eg. "fetch_from": "batch_name.project_code" fetch_from look like this. which means batch_name is Link field and project_code is fieldname of that doctype which is linked to batch_name.
    # for getting Link doctype name we need all Link fieldtype fields objects.
    link_list = []

    # table_list is list of all the tables in the ERD
    table_list = []

    # connections_string_list is list of all the Link connections in the ERD in string format.
    # eg. salutation of lead doctype is link to salutation doctype then connection_string_list will have ['lead:salutation -> salutation:name;']
    connections_string_list = []

    # fetch_from_string_list is list of all the fetch_from connections in the ERD in string format just like connection_string_list.
    fetch_from_string_list = []

    for doctype in doctypes:
        data = frappe.get_meta(doctype).as_dict()
        json_list.append(data)
        # check if fieldtype is Link then add it to link_list
        link_list += [{**x, 'doctype': data.get('name')}
                      for x in data.get('fields') if x['fieldtype'] == 'Link']

    for doctype_data in json_list:
        # get_table function will return table string, connection_list, fetch_from
        table, connection_list, fetch_from = get_table(
            doctype_data, link_list, doctypes, child_tables, amended_from)
        table_list.append(table)
        connections_string_list += connection_list
        fetch_from_string_list += fetch_from

    # get_graph_string function will return graph string which is used to create graph
    graph_string = get_graph_string(
        table_list, connections_string_list, fetch_from_string_list)

    # create_graph function will create graph from graph_string
    create_graph(graph_string)

    return 'Success'


def create_graph(graph_string):
    # create graph from graph_string
    # format can be png, pdf, etc.
    # view=True will open the graph in default browser
    # erd is the name of the graph
    graph = graphviz.Source(graph_string)
    graph.format = 'png'
    graph.render('erd', view=True)


def get_table(data, link_list, doctypes, child_tables, amended_from):
    # data is doctype json data (meta data) link_list is list of all Link fieldtype fields objects and doctypes is list of all doctypes
    # get_table function will return table string, connection_list, fetch_from

    # table_element_list is row of the table in the ERD in string format.
    table_element_list = []

    # remove_fieldtype is list of fieldtype which we don't want to show in the ERD.
    remove_fieldtype = ['Column Break', 'Section Break', 'Tab Break']

    # connection_list is list of all the Link connections in the ERD in string format.
    connection_list = []

    # fetch_from is list of all the fetch_from connections in the ERD in string format just like connection_list.
    fetch_from = []
    for field in data.get("fields"):
        if field.get('fieldtype') not in remove_fieldtype:
            # add each field as a row in the table
            if field.get('is_custom_field'):
                table_element_list.append(
                    f'<tr><td bgcolor="#FEF3E2" port="{field.get("fieldname")}">{field.get("label")}</td></tr>')
            else:
                table_element_list.append(
                    f'<tr><td port="{field.get("fieldname")}">{field.get("label")}</td></tr>')
        if field.get("fieldtype") == "Link" and (amended_from or field.get("fieldname") != "amended_from"):
            # get_connection function will return connection string
            connection_data = get_connection(field, data.get("name"), doctypes)
            if connection_data:
                connection_list.append(connection_data)
        if field.get("fieldtype") == "Table" and child_tables:
            connection_data = get_connection(field, data.get("name"), doctypes)
            if connection_data:
                connection_list.append(connection_data)
        if field.get("fetch_from") != None:
            # get_fetch_from function will return fetch_from string
            fetch_data = get_fetch_from(field, data.get(
                "name"), link_list, doctypes)
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
    # data is Link fieldtype field object, doctype_name is doctype name and doctypes is list of all doctypes
    # get_connection function will return connection string
    if data.get("options") in doctypes:
        source = "".join(c if c.isalnum() else "_" for c in doctype_name).lower()
        dest = "".join(c if c.isalnum() else "_" for c in data.get("options")).lower()
        connection_string = f"""{source}:{data.get('fieldname')} -> {dest}:name;"""
        return connection_string
    return None


def get_fetch_from(data, doctype_name, link_list, doctypes):
    # data is field object of doctype which have fetch_from field, doctype_name is doctype name, link_list is list of all Link fieldtype fields objects and doctypes is list of all doctypes
    # get_fetch_from function will return fetch_from string
    for link in link_list:
        if link.get("fieldname") == data.get("fetch_from").split(".")[0] and link.get('options' in doctypes):
            source = "".join(c if c.isalnum() else "_" for c in link.get('doctype')).lower()
            dest = "".join(c if c.isalnum() else "_" for c in link.get('options')).lower()
            fetch_string = f"""{source}:{data.get('fieldname')} -> {dest}:{data.get("fetch_from").split(".")[1]} [style="dashed"];"""
            return fetch_string
    return None


def get_graph_string(table_list, connections_string_list, fetch_from_string_list):
    # join all the table, connection and fetch_from string to get graph string
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
            <tr><td>Custom Fields</td>
            <td cellpadding="2"><table border="1" cellpadding="8" cellspacing="0" >
            <tr><td bgcolor="#FEF3E2"></td></tr></table></td></tr>
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
