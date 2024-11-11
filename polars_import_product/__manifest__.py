# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Polars Import Product",
    "version": "18.0.1.0.0",
    "summary": "Allow to import products related data from polars dataframe",
    "category": "Data",
    "license": "AGPL-3",
    "author": "Akretion, Odoo Community Association (OCA)",
    "development_status": "Alpha",
    "website": "https://github.com/OCA/server-backend",
    "maintainers": ["bealdav"],
    "depends": [
        "product",
        "polars_db_process",
    ],
    "data": [
        "data/model_map.xml",
    ],
    "installable": True,
}
