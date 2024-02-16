## Frappe ERD Generator

ERD generator for frappe doctypes

#### Download

```bash
$ bench get-app https://github.com/The-Commit-Company/frappe_er_generator.git
```

#### Install

```bash
$ bench --site site_name install-app frappe_er_generator
```

1. Call `get_erd` function for generating ERD by passing list of doctypes as argument. Other arguments include `child_tables` to include child table links as well as `amended_from` to include that field.

path = `api/method/frappe_er_generator.frappe_er_generator.er_generator.get_erd?doctypes = ["DocType1", "DocType2"]`

2. Call `get_whitelist_methods_in_app` function for fetching all whitelisted methods in app, by passing app name as argument. `app` is argument name.

#### Note:

If got error while calling API - "RuntimeError: Make sure the Graphviz executables are on your system's path" after installing Graphviz 2.38, them install graphviz in macos using brew

```bash
$ brew install graphviz
```

#### Output:

1. ERD in PNG format

![erd](https://user-images.githubusercontent.com/59503001/231471200-7717c3d4-75f5-45b2-8c2c-84d07ddd865b.png)


2. Output of `get_whitelist_methods_in_app`

<img width="1440" alt="image" src="https://user-images.githubusercontent.com/59503001/231189481-3d0a39b9-3cf4-49e1-a456-706ff700138f.png">

#### License

MIT
