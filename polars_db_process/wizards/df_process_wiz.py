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
        self.df_source_id.time = end_time - start_time
        return res

    def _pre_process_query(self):
        "You may inherit to set your own behavior"
        if not self.df_source_id.query_id:
            raise ValidationError(_("Missing database query in your dataframe source "))
        self._process_query()

    def _process_query(self):
        self.ensure_one()
        query = self.df_source_id._get_sql()
        try:
            df = self.df_source_id.query_id.db_conf_id._read_sql(query)
        except Exception as err:
            raise ValidationError(_(f"Error {err}\n\nSql:\n{query}")) from err
        if self.model_map_id:
            if self.model_map_id.action == "import":
                self._odoo_data_import(df)

    def _odoo_data_import(self, df):
        model = self.model_map_id.model_id.model
        if df.is_empty():
            raise ValidationError(f"No data in dataframe from model {model}")
        method = f"_import_df_{model.replace('.', '_')}"
        if hasattr(self.env.get(model), method):
            df, count = getattr(self.env.get(model), method)(df, self.df_source_id)
            self.df_source_id.count = count
            return
        raise ValidationError(_(f"{method} doesn't exist for the model {model}"))


def log(data, string=""):
    logger.warning(f"{string}: {data}")
