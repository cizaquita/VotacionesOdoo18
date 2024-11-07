from odoo import api, fields, models
import pytz

class Campus(models.Model):
    _name = 'uniacme_votes.campus'
    _description = 'Sede'

    name = fields.Char(string='Nombre de la sede', required=True)
    description = fields.Text(string='Descripción de la sede')
    timezone = fields.Selection(
        selection=[(tz, tz) for tz in sorted(pytz.all_timezones)],
        string='Zona horaria de la sede',
        required=True,
        help='Seleccione la zona horaria en la que se encuentra la sede'
    )