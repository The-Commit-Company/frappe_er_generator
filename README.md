## Frappe Er Generator

ERD generator for frappe doctypes

#### License

MIT

#### Installation

```bash
$ bench get-app frappe_er_generator
```

Call `get_erd` function for generating ERD by passing list of doctypes as argument.

path = `api/method/frappe_er_generator.frappe_er_generator.er_generator.get_erd?doctypes = ["DocType1", "DocType2"]`

#### Note:

If got error while calling API - "RuntimeError: Make sure the Graphviz executables are on your system's path" after installing Graphviz 2.38, them install graphviz in macos using brew

```bash
$ brew install graphviz
```
