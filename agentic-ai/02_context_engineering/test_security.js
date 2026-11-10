const assert = require('assert');
const { authenticateUser } = require('./src/legacy_auth');

console.log("=== Starting security test suite (Task 2) ===\n");

try {
    // Test 1 : Normal behavior must always continue to work (non-regression)
    console.log("Test 1 : Legitimate connection...");
    const validLogin = authenticateUser("dev@entreprise.com", "password123");
    assert.strictEqual(validLogin.success, true, "Error: Standard login was broken by the refactoring.");
    console.log("-> OK\n");

    // Test 2 : SQL injection attempt
    console.log("Test 2 : SQL injection attempt...");
    const maliciousEmail = "admin@entreprise.com' OR '1'='1";
    const maliciousPassword = "hack";
    
    const hackedLogin = authenticateUser(maliciousEmail, maliciousPassword);

    // The assertion requires the login to fail. If the code is vulnerable, `hackedLogin.success` evaluates to "true," which triggers the error.
    assert.strictEqual(
        hackedLogin.success, 
        false, 
        "FAILLE CRITIQUE DÉTECTÉE : L'injection SQL a réussi ! Votre prompt IA n'a pas sécurisé la requête."
    );
    
    console.log("-> OK\n");
    console.log("✅ PASSED: The code has been properly secured by the AI ​​agent.");

} catch (error) {
    console.error(`❌ FAILED: ${error.message}`);
    console.log("\n-> Relaunch your Agent with better instructions to fix the flaw.");
    process.exit(1);
}