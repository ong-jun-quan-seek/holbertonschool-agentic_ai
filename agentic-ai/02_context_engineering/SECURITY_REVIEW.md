# 1. Iterative Refactoring and Securing of an Injection Vulnerability

## Prompt used for the fix
```
You are a senior software developer and security expert. 
The project uses JavaScript and node for validation. 

Task: The current @legacy_auth.js has SQL injection vulnerability. Fix it using a prepared or parameterized query without changing the function signature or the return object on success, so as to preserve Test 1. 
Constraint: The existing functional behavior validated by @test_security.js must be preserved. 
```

## Short summary of the identified vulnerability

SQL injection via string concatenation. authenticateUser built the SQL statement by interpolating email and password directly into the query ("... WHERE email = '" + email + "' AND password = '" + password + "'"). An attacker could break out of the string literal (e.g. admin@entreprise.com' OR '1'='1) and alter query logic. The simulated DB treated that pattern as a successful bypass and returned a fake admin row.

## Short summary of changes porposed by the Agent

1. Replaced dynamic SQL concatenation with a parameterized query: SELECT * FROM users WHERE email = ? AND password = ?, passing [email, password] as bound parameters so user input is never interpreted as SQL syntax.
2. Adjusted the in-file db.query simulator to authenticate by comparing bound parameter values to known credentials, mirroring how a real driver would execute prepared statements.

## Test Result

**Before:** 
```
=== Starting security test suite (Task 2) ===

Test 1 : Legitimate connection...
[DB ENGINE] Exécution de la requête : SELECT * FROM users WHERE email = 'dev@entreprise.com' AND password = 'password123'
-> OK

Test 2 : SQL injection attempt...
[DB ENGINE] Exécution de la requête : SELECT * FROM users WHERE email = 'admin@entreprise.com' OR '1'='1' AND password = 'hack'
❌ FAILED: FAILLE CRITIQUE DÉTECTÉE : L'injection SQL a réussi ! Votre prompt IA n'a pas sécurisé la requête.

true !== false
```

**After:**
=== Starting security test suite (Task 2) ===

Test 1 : Legitimate connection...
[DB ENGINE] Exécution de la requête : SELECT * FROM users WHERE email = ? AND password = ?
[DB ENGINE] Paramètres liés : ["dev@entreprise.com","password123"]
-> OK

Test 2 : SQL injection attempt...
[DB ENGINE] Exécution de la requête : SELECT * FROM users WHERE email = ? AND password = ?
[DB ENGINE] Paramètres liés : ["admin@entreprise.com' OR '1'='1","hack"]
-> OK

✅ PASSED: The code has been properly secured by the AI ​​agent.