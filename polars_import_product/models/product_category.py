from odoo import _, api, models
from odoo.exceptions import ValidationError

from odoo.addons.polars_process import slug_me


class ProductCategory(models.Model):
    _inherit = "product.category"

    @api.model
    def _import_df_product_category(self, df, dfsource):
        vals_list = df.to_dicts()
        mapper = {}
        uidstring_prefix = dfsource.query_id._get_params().get("uidstring")
        if not uidstring_prefix:
            raise ValidationError(_(f"Missing 'uidstring' in sql in {dfsource.name}"))
        for vals in vals_list:
            uidstring = slug_me(vals.pop("id"))
            real_vals = self.env["df.import"]._filter_useful_vals(self._name, vals)
            rebel_fields = self.env["df.import"]._skip_rebel_fields(
                self._name, real_vals
            )
            if "parent_id" in real_vals:
                real_vals["parent_id"] = mapper.get(f"{vals['parent_id']}")
            rec = self.create(real_vals)
            self.env["df.import"]._set_unique_idstring(uidstring, rec, self._name)
            mapper[uidstring] = rec.id
            self.env["df.import"].env["df.import"]._process_touchy_fields(
                rec, rebel_fields
            )
        return df, len(vals_list)
