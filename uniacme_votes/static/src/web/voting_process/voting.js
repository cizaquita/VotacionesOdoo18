function updateCandidateImage() {
    // Obtiene el ID del candidato seleccionado
    const candidateSelect = document.getElementById('candidate_id');
    const candidateId = candidateSelect.value;

    // Verifica si hay un candidato seleccionado
    if (candidateId) {
        // Realiza una solicitud AJAX para obtener la imagen del candidato
        fetch(`/voting/image/${candidateId}`)
            .then(response => response.json())
            .then(data => {
                const imageContainer = document.getElementById('candidate-image-container');
                const candidateImage = document.getElementById('candidate-image');
                
                // Muestra la imagen del candidato
                if (data.image) {
                    candidateImage.src = `data:image/png;base64,${data.image}`;
                    imageContainer.style.display = 'block';
                } else {
                    imageContainer.style.display = 'none';
                }
            })
            .catch(error => console.error('Error al cargar la imagen del candidato:', error));
    }
}