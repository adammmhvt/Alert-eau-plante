document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("plantForm");

    form.addEventListener("submit", (event) => {

        // Récupérer les valeurs
        const tempMin = parseFloat(form.temp_min.value);
        const tempMax = parseFloat(form.temp_max.value);
        const humMin = parseFloat(form.hum_min.value);
        const humMax = parseFloat(form.hum_max.value);

        let message = "";

        // Vérif température
        if (tempMax < tempMin) {
            message += "La température maximale doit être supérieure à la minimale.\n";
        }

        // Vérif humidité
        if (humMax < humMin) {
            message += "L'humidité maximale doit être supérieure à la minimale.\n";
        }

        // Si erreur → empêcher l’envoi + afficher message
        if (message !== "") {
            event.preventDefault();
            alert(message);
        }
    });
});
