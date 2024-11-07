from odoo import models, fields, api
from odoo.exceptions import ValidationError

class VotingProcessLine(models.Model):
    _name = 'uniacme_votes.voting_process_line'
    _description = 'Línea de Proceso de Votación'
    
    voting_process_id = fields.Many2one('uniacme_votes.voting_process', string="Proceso de Votación", required=True)
    candidate_id = fields.Many2one(
        'res.partner',
        string='Candidato',
        domain=[('is_student', '=', False), ('is_candidate', '=', True)], 
        help='Candidato que participa en la votación (debe ser candidato y no estudiante)'
    )
    candidate_photo = fields.Binary(
        string='Foto del candidato', 
        help="Imagen del candidato seleccionado en la votación"
    )
    voter_ids = fields.Many2many(
        'res.partner',
        string='Votantes',
        domain=[('is_student', '=', True)],
        help="Votantes participantes en la votación (deben ser estudiantes)"
    )
    
    vote_count = fields.Integer(
        string='Cantidad de votos', 
        compute='_compute_vote_count', 
        store=True, 
        help="Cantidad de votos del candidato en esta votación", 
        readonly=True
    )

    @api.depends('voter_ids')
    def _compute_vote_count(self):
        for record in self:
            record.vote_count = len(record.voter_ids)

    @api.onchange('candidate_id')
    def _onchange_candidate_id(self):
        if self.candidate_id:
            self.candidate_photo = self.candidate_id.image_1920
        else:
            self.candidate_photo = False

    @api.constrains('candidate_id', 'voting_process_id')
    def _check_unique_candidate_per_voting_process(self):
        for record in self:
            existing_lines = self.search([
                ('voting_process_id', '=', record.voting_process_id.id),
                ('candidate_id', '=', record.candidate_id.id),
                ('id', '!=', record.id)
            ])
            if existing_lines:
                raise ValidationError(
                    "El candidato {} ya está registrado en este proceso de votación.".format(record.candidate_id.display_name)
                )