import logging
import time

from odoo import _, models
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)


class DfProcessWiz(models.TransientModel):
    _inherit = "df.process.wiz"

    def _pre_process(self):
        start_time = time.time()
        res = super()._pre_process()
        if not self.file:
            self._pre_process_query()
        end_time = time.time()
        # Calculate elapsed time
        elapsed_time = end_time - start_time
        self.df_source_id.time = elapsed_time
        # print("Elapsed time: ", elapsed_time)
        # breakpoint()  # import pdb; pdb.set_trace()
        return res

    def _pre_process_query(self):
        "You may inherit to set your own behavior"
        if not self.df_source_id.query_id:
            raise ValidationError(_("Missing database query in your dataframe source "))
        self._process_query()

    def _process_query(self):
        self.ensure_one()
        query = self.df_source_id._get_sql()
        df = self.df_source_id.query_id.db_conf_id._read_sql(query)
        if self.model_map_id:
            if self.model_map_id.action == "import":
                self._odoo_data_import(df)

    def _odoo_data_import(self, df):
        model = self.model_map_id.model_id.model
        if df.is_empty():
            raise ValidationError(f"No data in dataframe from model {model}")
        method = f"_import_df_{model.replace('.', '_')}"
        if hasattr(self.env.get(model), method):
            return getattr(self.env.get(model), method)(df, self.df_source_id)
        raise ValidationError(_(f"{method} doesn't exist for the model {model}"))
        # if model == "res.partner":
        #     df = self.env["res.partner"]._process_partner_df(df)
        # if "livr.sql" in self.df_source_id.name:
        #     parents = {
        #         x.name: x.res_id
        #         for x in self._get_ir_model_data("res.partner", "societe")
        #     }
        # if model == "product.product":
        #     df = self.env["product.product"]._process_product_df(
        # df, self.df_source_id)
        # for vals in vals_list:
        # keeps = self._skip_rebel_fields(model, vals)
        # uidstring = slug_me(vals.pop("id"))
        # nvals = self.env["df.import"]._filter_useful_vals(self, self._name, vals)
        # if "categ_id" in nvals:
        #     nvals["categ_id"] = categs.get(nvals["categ_id"]) or 1
        # if "parent_id" in nvals:
        #     # here for product.category
        #     # TODO move this specific behavior elsewhere
        #     if model == "res.partner":
        #         nvals["parent_id"] = parents.get(nvals["parent_id"])
        #     if model == "product.category":
        #         nvals["parent_id"] = mapper.get(nvals["parent_id"])
        # rec = self.env[model].create(nvals)
        # if model == "product.category":
        #     mapper[uidstring] = rec.id
        # self.env["df.import"]._set_unique_idstring(uidstring, rec, model)
        # self.env["df.import"]._process_touchy_fields(rec, keeps)


def log(data, string=""):
    logger.warning(f"{string}: {data}")
