// Simulation très basique d'un connecteur de base de données
const db = {
    query: (sql, params = []) => {
        console.log(`[DB ENGINE] Exécution de la requête : ${sql}`);
        if (params.length > 0) {
            console.log(`[DB ENGINE] Paramètres liés : ${JSON.stringify(params)}`);
        }

        const [boundEmail, boundPassword] = params;
        if (
            boundEmail === 'dev@entreprise.com' &&
            boundPassword === 'password123'
        ) {
            return [{ id: 1, role: 'admin', email: 'dev@entreprise.com' }];
        }
        return [];
    }
};

/**
 * Fonction d'authentification legacy
 * Requête paramétrée : email et mot de passe sont liés, jamais concaténés dans le SQL.
 */
function authenticateUser(email, password) {
    const sql = 'SELECT * FROM users WHERE email = ? AND password = ?';
    const results = db.query(sql, [email, password]);

    if (results.length > 0) {
        return { success: true, user: results[0] };
    }
    return { success: false, message: "Identifiants invalides" };
}

module.exports = { authenticateUser };
