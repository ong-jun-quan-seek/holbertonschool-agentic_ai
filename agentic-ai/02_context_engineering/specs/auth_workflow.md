Feature: User Authentication
  Scenario: Successful login with valid credentials
    Given a user with the email "dev@entreprise.com" exists in the database
    When the user submits their valid credentials
    Then the system must generate a valid JWT token.