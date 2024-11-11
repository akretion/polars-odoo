import logging

from odoo import models

_logger = logging.getLogger(__name__)


class ModelMap(models.Model):
    _inherit = "model.map"

    def _remove_uidstring_related_records(self):
        if not self:
            active_ids = self.env.context.get("active_ids")
            if active_ids:
                self = self.browse(self.env.context.get("active_ids"))
        for rec in self:
            im_data = self.env["ir.model.data"].search(
                [
                    ("model", "=", rec.model_id.model),
                    ("module", "=", self._get_uidstring_module_name()),
                ]
            )
            _logger.info(
                f" >>> Remove IrModelData model '{rec.model_id.model}' "
                f"module'{self._get_uidstring_module_name()}' Count {len(im_data)}"
            )
            if im_data:
                record_ids = [int(x.split(",")[1]) for x in im_data.mapped("reference")]
                _logger.info(f"  >> to remove {len(record_ids)}")
                self.env[rec.model_id.model].browse(record_ids).unlink()
        return True

    def _get_uidstring_module_name(self):
        # TODO move to static method
        return "polars"

    def _get_touchy_fields_to_import(self):
        """inherit me
         Some fields may break your process and could be benefit
         of a specific process. We have to know them
        i.e. {"res.partner": ["vat"]}
        """
        # TODO move to static method
        return {}
