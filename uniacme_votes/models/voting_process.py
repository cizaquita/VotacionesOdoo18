from odoo import models, fields, api
from odoo.exceptions import ValidationError

class VotingProcess(models.Model):
    _name = 'uniacme_votes.voting_process'
    _description = 'Proceso de Votación'
    _inherit = ['mail.thread.main.attachment', 'mail.activity.mixin']
    
    name = fields.Char(string='Nombre', required=True, help="Nombre de la votación")
    description = fields.Char(string='Descripción de la votación', required=True, help="Descripción de la votación")
    voting_start = fields.Datetime(string='Inicio de votación', required=True, help="Fecha y hora de inicio de la votación")
    voting_end = fields.Datetime(string='Fin de votación', required=True, help="Fecha y hora de fin de la votación")
    
    voting_line_ids = fields.One2many('uniacme_votes.voting_process_line', 'voting_process_id', string="Líneas de votación", tracking=True)
    
    voting_process_status = fields.Selection([
        ('draft', 'Borrador'),
        ('in_progress', 'En Proceso'),
        ('closed', 'Cerrada'),
    ], default="draft", string="Estado",
        store=True, index=True, tracking=True,
        group_expand=True)
    
    total_votes = fields.Integer(
        string='Total de votos',
        compute='_compute_total_votes',
        store=True
    )

    @api.depends('voting_line_ids.vote_count')
    def _compute_total_votes(self):
        for record in self:
            total = sum(line.vote_count for line in record.voting_line_ids)
            record.total_votes = total

    @api.constrains('voting_start', 'voting_end')
    def _check_voting_period(self):
        for record in self:
            if record.voting_start >= record.voting_end:
                raise ValidationError("La fecha de inicio de votación debe ser anterior a la fecha de fin.")
    
    def action_start_voting(self):
        """Iniciar la votación si está en borrador y las fechas son válidas."""
        for record in self:
            if record.voting_process_status != 'draft':
                raise ValidationError("Solo las votaciones en estado 'Borrador' pueden ser iniciadas.")
            if fields.Datetime.now() < record.voting_start or fields.Datetime.now() > record.voting_end:
                raise ValidationError("El período de votación debe estar activo para iniciar la votación.")
            record.voting_process_status = 'in_progress'
    
    def action_close_voting(self):
        """Cerrar la votación si está en proceso."""
        for record in self:
            if record.voting_process_status == 'in_progress':
                record.voting_process_status = 'closed'
            else:
                raise ValidationError("Solo las votaciones en estado 'En Proceso' pueden ser cerradas.")
    
    @api.model
    def start_multiple_votings(self, voting_ids):
        if not voting_ids:
            raise ValueError("No se proporcionaron IDs para iniciar las votaciones.")

        votings = self.browse(voting_ids)
        votings.filtered(lambda v: v.voting_process_status == 'draft').action_start_voting()


