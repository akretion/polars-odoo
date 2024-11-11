import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class DfImport(models.Model):
    _name = "df.import"
    _description = "Helper methods for ERP import"

    @api.model
    def _filter_useful_vals(self, model, vals):
        return {
            x: val
            for x, val in vals.items()
            if x.lower() in self.env[model]._fields.keys()
        }

    @api.model
    def _skip_rebel_fields(self, model, vals):
        rebels = {}
        rebel_model = self.env["model.map"]._get_touchy_fields_to_import().get(model)
        if rebel_model:
            for key in self.env["model.map"]._get_touchy_fields_to_import().get(model):
                if key in vals:
                    rebels[key] = vals.pop(key)
        return rebels

    def _set_unique_idstring(self, uidstring, record, model):
        """Create Unique Id String also know as XmlId in the Odoo world,
        even if not really xml ;-)"""
        self.env["ir.model.data"].create(
            {
                "res_id": record.id,
                "model": model,
                "module": self.model_map_id._get_uidstring_module_name(),
                "name": uidstring,
                "noupdate": False,
            }
        )

    def _get_ir_model_data(self, model, string, module=None):
        module = module or self.env["db.config"]._set_uidstring_module_name()
        return self.env["ir.model.data"].search(
            [
                ("module", "=", module),
                ("model", "=", model),
                ("name", "ilike", f"%{string}%"),
            ]
        )

    def _process_touchy_fields(self, record, touchy):
        """Override Suggestion:
        self._touchy_fields_fallback(record, touchy)
        or any other alternative
        """

    def _touchy_fields_fallback(self, record, touchy):
        for key in touchy:
            try:
                record[key] = touchy[key]
            except Exception:
                _logger.warning(f"\n\n\n\n\nCarefull here {touchy[key]}")
                continue
