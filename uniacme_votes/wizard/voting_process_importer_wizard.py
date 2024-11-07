from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64
import csv
from io import StringIO

class VotingProcessImporterWizard(models.TransientModel):
    _name = 'uniacme_votes.voting_process_importer_wizard'
    _description = 'Wizard para Importar Procesos de Votaciones'

    file = fields.Binary("Archivo a Importar")
    filename = fields.Char("Nombre del Archivo", readonly=True)
    
    def download_template_example(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/voting/download_template',
            'target': 'self',
        }

    def import_voting_processes(self):
        """Importa los procesos de votación desde el archivo CSV cargado."""
        if not self.file:
            raise ValidationError("Debe cargar un archivo CSV para importar.")

        decoded_file = base64.b64decode(self.file).decode('utf-8')
        csv_data = csv.reader(StringIO(decoded_file), delimiter=',')

        # Validar encabezados del archivo
        headers = next(csv_data, None)
        if headers != ['Nombre', 'Descripción', 'Fecha Inicio', 'Fecha Fin']:
            raise ValidationError("El archivo CSV debe contener las columnas: Nombre, Descripción, Fecha Inicio, Fecha Fin.")

        # Insertar registros en la base de datos
        values_to_insert = []
        for row in csv_data:
            if len(row) < 4:
                continue  # Saltar filas incompletas
            values_to_insert.append({
                'name': row[0],
                'description': row[1],
                'voting_start': row[2],
                'voting_end': row[3],
                'voting_process_status': 'draft'
            })

        # Insertar registros en la base de datos usando SQL
        if values_to_insert:
            query = """
                INSERT INTO uniacme_votes_voting_process (name, description, voting_start, voting_end, voting_process_status, create_date, write_date)
                VALUES (%(name)s, %(description)s, %(voting_start)s, %(voting_end)s, %(voting_process_status)s, NOW(), NOW())
            """
            self.env.cr.executemany(query, values_to_insert)

        # Redirigir al modelo voting_process a la vista de lista después de la importación
        return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Importación Completa',
                    'message': 'Se han importado los procesos de votación exitosamente.',
                    'sticky': False,
                    'next': {
                        'res_model': 'uniacme_votes.voting_process',
                        'type': 'ir.actions.act_window',
                        'view_mode': 'list',
                        'views': [[False, 'list'], [False, 'form']],
                    },
            }
        }
