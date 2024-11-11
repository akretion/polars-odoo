from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval

MODULE = __name__[12 : __name__.index(".", 13)]

HELP = """Populated by Sql files which contains comments on first lines:
Create an new record to see an example.
"""
REQUIRED_KEYS = ["model_code", "db_conf", "name"]

PARAMS = (
    "{'model_code': 'my model.map code', 'db_conf': 'my conf', "
    "'name': 'name of query', 'sequence': 5,\n"
    "'where': [\"myfield like 'A%'\", 'active = 1']}\n"
    f"# Required keys are {REQUIRED_KEYS}"
)


class DfQuery(models.Model):
    _name = "df.query"
    _inherit = ["upsert.mixin"]
    _description = "Sql query"
    _order = "sequence ASC"

    name = fields.Char()
    query = fields.Text(
        help="SQL query coming from .sql files placed in 'my_module/data/df'"
    )
    params = fields.Char(
        string="File Parameters",
        default=PARAMS,
        readonly=True,
        help=HELP,
    )
    sequence = fields.Integer()
    db_conf_id = fields.Many2one(
        comodel_name="db.config", required=True, help="Database Configuration"
    )

    def _get_params(self):
        self.ensure_one()
        try:
            params = safe_eval(self.params)
        except Exception as err:
            raise ValidationError(
                _(f"Params '{self.name}' evaluation failed\n{self.params}")
            ) from err
        return params
