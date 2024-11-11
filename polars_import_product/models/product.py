from odoo import api, models

from odoo.addons.polars_process import slug_me


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _import_df_product_product(self, df, source):
        categs = {
            x.name: x.res_id
            for x in self._get_ir_model_data("product.category", "cat-")
        }
        vals_list = df.to_dicts()
        cpt = 0
        for vals in vals_list:
            nvals = self.env["df.import"]._filter_useful_vals(self._name, vals)
            rebel_fields = self.env["df.import"]._skip_rebel_fields(self._name, vals)
            if "categ_id" in nvals:
                nvals["categ_id"] = categs.get(nvals["categ_id"]) or 1
            rec = self.create(nvals)
            self.env["df.import"]._process_touchy_fields(rec, rebel_fields)
            cpt += 1
        return df


class ProductCategory(models.Model):
    _inherit = "product.category"

    @api.model
    def _import_df_product_category(self, df, source):
        vals_list = df.to_dicts()
        mapper = {}
        cpt = 0
        parents = {
            x.name: x.res_id for x in self._get_ir_model_data("res.partner", "societe")
        }
        for vals in vals_list:
            uidstring = slug_me(vals.pop("id"))
            nvals = self.env["df.import"]._filter_useful_vals(self._name, vals)
            rebel_fields = self.env["df.import"]._skip_rebel_fields(self._name, vals)
            if "parent_id" in nvals:
                nvals["parent_id"] = parents.get(nvals["parent_id"])
            rec = self.create(nvals)
            mapper[uidstring] = rec.id
            self.env["df.import"]._process_touchy_fields(rec, rebel_fields)
            cpt += 1
        return df
