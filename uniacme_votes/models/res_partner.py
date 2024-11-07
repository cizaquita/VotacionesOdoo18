# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_candidate = fields.Boolean(string='Es Candidato', help='Marque si es candidato')
    is_student = fields.Boolean(string='Es Estudiante', help='Marque si es estudiante')
    campus_id = fields.Many2one('uniacme_votes.campus', string='Sede asociada', help='Seleccione la sede asociada')
    career = fields.Char(string='Carrera a la que pertenece', help='Especifique la carrera')
    id_number = fields.Char(string='Nro. Identificación', help="Número de identificación.", required=True)
    
    @api.constrains('is_candidate', 'is_student')
    def _check_is_candidate_is_student(self):
        for record in self:
            if record.is_candidate and record.is_student:
                raise ValidationError("Un registro no puede ser 'Candidato' y 'Estudiante' al mismo tiempo.")
            
    @api.constrains('id_number')
    def check_unique_id_number(self):
        for record in self:
            if record.id_number:
                # Excluir el registro actual de la búsqueda de duplicados
                exist_res_partner = self.env['res.partner'].search([
                        ('id_number', '=', record.id_number),
                        ('is_student', '=', record.is_student), 
                        ('is_candidate', '=', record.is_candidate),
                        ('id', '!=', record.id)
                    ], limit=1)
                
                if exist_res_partner:
                    raise ValidationError("Ya existe un registro con el número de identificación ingresado.")
