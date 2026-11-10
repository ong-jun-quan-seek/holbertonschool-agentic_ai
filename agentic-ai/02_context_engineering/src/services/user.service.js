const userRepository = require('../repositories/user.repository');

class UserService {
    async getUserProfile(email) {
        const user = userRepository.findByEmail(email);
        if (!user) {
            throw new Error("User not found in the system");
        }
        return user;
    }
}

module.exports = new UserService();