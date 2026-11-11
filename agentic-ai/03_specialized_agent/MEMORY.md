# PROJECT THESIS: Agentic E-Commerce

## 🛠️ Stack & Conventions
- Environment: Node.js (Vanilla JavaScript)
- Testing framework: Jest
- No TypeScript for this microservice.

## 📐 Architectural Decisions (Background)
- Price handling requires caution. While the main application operates using cents, the current `cart_calculator.js` is a legacy component that returns values ​​in Euros with two decimal places. This is a known instance of technical debt.
- **Absolute QA Rule:** Refactoring or modifying the business logic within the `/src` directory is strictly prohibited during the test generation phase. The QA Agent’s scope is limited exclusively to testing.

## 📊 Current Status & Next Steps
- Critical requirement: Establish a robust suite of unit tests for the cart calculator before any migration takes place.