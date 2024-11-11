# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Polars Database Process",
    "version": "18.0.1.0.0",
    "summary": "Allow to create a Polars dataframe from db.query and "
    "check it and process it according to rules",
    "category": "Reporting",
    "license": "AGPL-3",
    "author": "Akretion, Odoo Community Association (OCA)",
    "development_status": "Alpha",
    "website": "https://github.com/OCA/server-backend",
    "maintainers": ["bealdav"],
    "depends": [
        "polars_process",
    ],
    "external_dependencies": {
        "python": [
            "connectorx",
            "phonenumbers",
        ]
    },
    "data": [
        "security/ir.model.access.xml",
        "wizards/df_process_wiz.xml",
        "views/model_map.xml",
        "views/field_map.xml",
        "views/df_source.xml",
        "views/df_query.xml",
        "views/db_config.xml",
        "data/action.xml",
        # "data/demo.xml",  # TODO remove
    ],
    "demo": [
        "data/demo.xml",
    ],
    "installable": True,
}
