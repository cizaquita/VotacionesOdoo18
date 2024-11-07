import base64
from odoo import http
from odoo.http import request

class VotingController(http.Controller):

    @http.route('/voting/login', type='http', auth='public', website=True)
    def voting_login(self, **kwargs):
        """Servir la vista de inicio de sesión."""
        request.session['student_id'] = False
        return request.render('uniacme_votes.voting_login_template')

    @http.route('/voting/authenticate', type='http', auth='public', methods=['POST'], website=True)
    def voting_authenticate(self, id_number, **kwargs):
        """Petición de autenticación por nro de identificación."""
        student = request.env['res.partner'].sudo().search([
            ('id_number', '=', id_number), 
            ('is_student', '=', True)
        ], limit=1)
        if student:
            request.session['student_id'] = student.id
            return request.redirect('/voting/select')
        else:
            return request.redirect('/voting/login')

    @http.route('/voting/select', type='http', auth='public', website=True)
    def voting_select(self, **kwargs):
        """Servir la vista de votación."""
        student_id = request.session.get('student_id')
        if not student_id:
            return request.redirect('/voting/login')

        student = request.env['res.partner'].sudo().browse(student_id)
        
        all_voting_processes = request.env['uniacme_votes.voting_process'].sudo().search([
            ('voting_process_status', '=', 'in_progress')
        ])
        
        voting_processes = all_voting_processes.filtered(lambda process: not any(
            student.id in voting_line.voter_ids.ids for voting_line in process.voting_line_ids
        ))

        return request.render('uniacme_votes.voting_select_template', {
            'voting_processes': voting_processes,
            'student': student
        })


    @http.route('/voting/image/<int:line_id>', type='http', auth='public', website=True)
    def voting_candidate_image(self, line_id, **kwargs):
        """Servir la imagen del candidato desde voting_process_line."""
        line = request.env['uniacme_votes.voting_process_line'].sudo().browse(line_id)
        if line and line.candidate_photo:
            image_data = base64.b64decode(line.candidate_photo)
            return request.make_response(image_data, headers=[('Content-Type', 'image/png')])
        else:
            placeholder_img = request.env['ir.http'].sudo().placeholder_image()
            return request.make_response(placeholder_img, headers=[('Content-Type', 'image/png')])
        

    @http.route('/voting/submit', type='http', auth='public', methods=['POST'], website=True)
    def voting_submit(self, **kwargs):
        student_id = request.session.get('student_id')
        if not student_id:
            return request.redirect('/voting/login')

        Vote = request.env['uniacme_votes.voting_process_line']

        for key, candidate_id in kwargs.items():
            if key.startswith("radio_candidate_selected_id_"):
                # Extraer el `voting_process_id` de la clave
                voting_process_id = int(key.split("_")[4])  # Obtiene el ID de votación de la clave
                voting_line = request.env['uniacme_votes.voting_process_line'].sudo().search([
                        ('voting_process_id', '=', voting_process_id), 
                        ('candidate_id', '=', int(candidate_id))
                    ], limit=1)
                if voting_line:
                    voting_line.sudo().write({
                            'voter_ids': [(4, student_id)]
                        })
                    
                    return request.render('uniacme_votes.voting_confirmation_template')
                else:
                    return request.render('uniacme_votes.voting_error_template')

    @http.route('/voting/download_template', type='http', auth="user")
    def download_template(self):
        # Generar el contenido de la plantilla en formato CSV
        csv_content = "Nombre,Descripción,Fecha Inicio,Fecha Fin\n" \
                      "Proceso 1,Descripción 1,2024-01-01 09:00:00,2024-01-01 17:00:00\n" \
                      "Proceso 2,Descripción 2,2024-01-02 09:00:00,2024-01-02 17:00:00\n"
        
        # Configurar la respuesta para descargar el archivo CSV
        return request.make_response(
            csv_content,
            headers=[
                ('Content-Type', 'text/csv'),
                ('Content-Disposition', 'attachment; filename="plantilla_votacion.csv"')
            ]
        )