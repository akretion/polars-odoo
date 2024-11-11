from pathlib import Path

from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_path
from odoo.tools.safe_eval import safe_eval

from odoo.addons.polars_process import slug_me

MODULE = __name__[12 : __name__.index(".", 13)]

HELP = """Supported: .xlsx  files and .sql
Sql files may contains a comment on first line captured by File Parameters field
to be mapped automatically with related objects, i.e:\n
{'map_model': 'my_delivery_address', 'db_conf': mydb, 'where': [{''}]}

"""


class DfSource(models.Model):
    _inherit = "df.source"

    name = fields.Char(help=HELP)
    query = fields.Text(string="Sql", related="query_id.query")
    where = fields.Char(readonly=True, help="Sql where condition")
    db_conf_id = fields.Many2one(
        comodel_name="db.config", help="Database Configuration"
    )
    query_id = fields.Many2one(comodel_name="df.query", help="Dataframe Query")

    def start(self):
        if self.state == "done":
            self.ValidationError(_("Reset before trigger import"))
        action = super().start()
        return action

    def _reset_process(self):
        res = super()._reset_process()
        mapp = self.model_map_id
        if mapp and mapp.action == "import":
            mapp._remove_uidstring_related_records()
        return res

    def _file_hook(self, vals, file, db_confs, model_map):
        "Map sql file with the right Odoo model via model_map and the right db.config"
        vals = super()._file_hook(vals, file, db_confs, model_map)
        if ".sql" in file and model_map:
            content = self._get_file(file).decode("utf-8")
            contents = content.split("\n")
            meta, sql = [], []
            if contents:
                meta_end = False
                for content in contents:
                    if content[:2] == "--" and not meta_end:
                        # collect first lines prefixed by '--'
                        meta.append(content.replace("--", ""))
                    else:
                        # collect other lines
                        meta_end = True
                        sql.append(content)
                if meta and sql:
                    meta = " ".join([str(x) for x in meta])
                    try:
                        meta = safe_eval(meta)
                    except Exception as err:
                        raise ValidationError(
                            _(
                                f"Error on '{file}' for params\n{meta}\n\n"
                                f"{err}\n\n/!\\ Check this dict format"
                            )
                        ) from err
                    # {'map_code': chinook customers', 'db_conf': Chinook}
                    keys = ("model_code", "db_conf", "name")
                    if [x for x in keys if x not in meta]:
                        raise ValidationError(
                            f"At least one of these keys {keys} "
                            f"is not in params: {vals['name']}"
                        )
                    model_map_id = model_map.get(meta["model_code"])
                    if not model_map_id:
                        raise ValidationError(
                            _(
                                f"model_code in {meta} for {file} "
                                f"doesn't match\n{model_map}"
                            )
                        )
                    query = "\n".join(sql)
                    for word in (
                        "select ",
                        "from ",
                        "group by ",
                        "having ",
                        "order by ",
                        "where ",
                    ):
                        query = query.replace(word, word.upper())
                    sequence = meta.get("sequence", "0")
                    qvals = {
                        "db_conf_id": db_confs.get(meta["db_conf"]),
                        "params": meta,
                        "query": query,
                        "name": meta["name"],
                        "sequence": int(sequence),
                    }
                    xml_id = slug_me(meta["name"])
                    self._upsert_record("df.query", xml_id, qvals, module="df_query")
                    query = self.env.ref(f"df_query.{xml_id}")
                    src = 0
                    where = meta.get("where", [""])
                    for source in where:
                        xml_id = slug_me(qvals["name"])
                        if src > 0:
                            xml_id = f"{xml_id}_{src}"
                        src_vals = {
                            "where": source,
                            "model_map_id": model_map_id,
                            "query_id": query.id,
                            "name": file,
                            "sequence": int(sequence),
                        }
                        src += 1
                        self._upsert_record(
                            "df.source", xml_id, src_vals, module="df_source"
                        )
        return vals

    def _get_sql(self):
        self.ensure_one()
        sql = False
        if self.query_id:
            sql = self.query
            if self.where:
                if "WHERE" in sql:
                    raise ValidationError(_("Where clause in 2 places: remove it one"))
                if "ORDER BY" in sql:
                    sql = sql.replace("ORDER BY", f"WHERE {self.where}\nORDER BY")
                else:
                    sql += self.where
        return sql

    def _get_db_confs(self):
        return {x.name: x.id for x in self.env["db.config"].search([])}

    def _populate(self):
        chinook = self.env.ref(f"{MODULE}.sqlite_chinook", raise_if_not_found=False)
        if chinook:
            # TODO fix
            # Demo behavior only
            path = Path(get_module_path(MODULE)) / "data/chinook.sqlite"
            chinook.string_connexion = f"sqlite://{str(path)}"
        return super()._populate()

    def _get_modules_w_df_files(self):
        res = super()._get_modules_w_df_files()
        if self.env.ref("base.module_polars_db_process").demo:
            res.update(
                {
                    "polars_db_process": {
                        "xmlid": "polars_db_process.contact_chinook",
                    }
                }
            )
        return res
