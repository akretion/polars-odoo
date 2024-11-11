from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _import_df_product_product(self, df, dfsource):
        uidstring_prefix = dfsource.query_id._get_params().get("uidstring")
        if not uidstring_prefix:
            raise ValidationError(_(f"Missing 'uidstring' in sql in {dfsource.name}"))
        categs = {
            x.name: x.res_id
            for x in self.env["df.import"]._get_ir_model_data(self._name, "cat-")
        }
        vals_list = df.to_dicts()
        cpt = 0
        for vals in vals_list:
            # if "categ_id" in nvals:
            #     nvals["categ_id"] = categs.get(nvals["categ_id"]) or 1
            real_vals = self.env["df.import"]._filter_useful_vals(self._name, vals)
            rebel_fields = self.env["df.import"]._skip_rebel_fields(
                self._name, real_vals
            )
            if "categ_id" in real_vals:
                real_vals["categ_id"] = categs.get(real_vals["categ_id"]) or 1
            rec = self.create(real_vals)
            self.env["df.import"].env["df.import"]._process_touchy_fields(
                rec, rebel_fields
            )
            cpt += 1
        return df, len(vals_list)
