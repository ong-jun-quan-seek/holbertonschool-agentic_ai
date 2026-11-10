class UserRepository {
    constructor() {
        // Simulation of an in-memory database
        this.db = new Map();
        this.db.set('dev@entreprise.com', { id: 1, name: 'Dev', role: 'admin' });
    }

    /**
     * Search for a user by their email
     * @param {string} email 
     * @returns {Object|null}
     */
    findByEmail(email) {
        return this.db.get(email) || null;
    }
}

module.exports = new UserRepository();