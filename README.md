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

Call `get_erd` function for generating ERD by passing list of doctypes as argument.

path = `api/method/frappe_er_generator.frappe_er_generator.er_generator.get_erd?doctypes = ["DocType1", "DocType2"]`

#### Note:

If got error while calling API - "RuntimeError: Make sure the Graphviz executables are on your system's path" after installing Graphviz 2.38, them install graphviz in macos using brew

```bash
$ brew install graphviz
```

#### Output:

![erd](https://user-images.githubusercontent.com/59503001/231124012-c8bb246e-9159-427c-8cd7-b36d3359e247.png)

#### License

MIT
