const userRepository = require('../repositories/user.repository');

class DataExportService {
    async exportUserData(email) {
        const user = userRepository.findByEmail(email);
        if (!user) {
            throw new Error("User not found in the system");
        }
        return {
            exportedAt: new Date().toISOString(),
            user,
        };
    }
}

module.exports = new DataExportService();
