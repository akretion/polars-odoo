import logging

import polars as pl

from odoo import api, models

logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _import_df_res_partner(self, df, source):
        rebel_fields = {}
        if "country" in df.columns:
            df = self._country_df_search(df, source)
            if "livr.sql" in source.name:
                parents = {
                    x.name: x.res_id
                    for x in self._get_ir_model_data("res.partner", "societe")
                }
        vals_list = df.to_dicts()
        cpt = 0
        for vals in vals_list:
            # uidstring = slug_me(vals.pop("id"))
            real_vals = self.env["df.import"]._filter_useful_vals(self._name, vals)
            rebel_fields = self.env["df.import"]._skip_rebel_fields(self._name, vals)
            if "parent_id" in real_vals:
                real_vals["parent_id"] = parents.get(real_vals["parent_id"])
            rec = self.create(real_vals)
            self.env["df.import"]._process_touchy_fields(rec, rebel_fields)
            cpt += 1
        return df

    @api.model
    def _country_df_search(self, df, source):
        # search country_id from country
        cntries = df.get_column("country").to_list()
        df = self._country_df_replacement(df, source)
        # new column filled with Null
        df = df.with_columns(country_id=pl.lit(None).cast(pl.Int32))
        cntries = df.get_column("country").to_list()
        cntry_id_by_names = {
            x.name: x.id
            for x in self.env["res.country"].search(
                [("name", "in", list(set(cntries)))]
            )
        }
        # fills new vals in column country_id
        cntry_ids = [cntry_id_by_names.get(x, None) for x in cntries]
        new_df = pl.DataFrame({"country_id": cntry_ids})
        # add new column
        df = df.update(new_df)
        # set(unknown_country.get_column('country').to_list())
        unknown_country = df.filter(pl.col("country_id").is_null()).select("country")
        if not unknown_country.is_empty():
            unknown_country = set(unknown_country.get_column("country").to_list())
            logger.warning(
                f"Unknown countries {unknown_country}",
            )
        df = df.drop(["country"])
        return df

    def _country_df_replacement(self, df, source):
        # https://docs.pola.rs/api/python/dev/reference/expressions/api/polars.Expr.replace_strict.html
        name = source.query_id.db_conf_id.name
        if name:
            replaces = getattr(self, f"_country_df_{name}_replacement")()
            if replaces:
                for pattern, replacem in replaces.items():
                    df = df.with_columns(
                        pl.col("country").str.replace(pattern, replacem)
                    )
        return df
