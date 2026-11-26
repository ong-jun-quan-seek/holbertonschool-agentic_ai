# Coding standards

## Constraints

- You are formally forbidden to use heavy frameworks (React/Vue).
- NEVER include any API tokens in the source code or push to GitHub. 

## Stacks

### HTML 

- Use semantic elements (<article>, <nav>, <main>) over generic <div>s to improve agent and accessibility understanding.
- Leave the styling to CSS instead of inline <style>, 
- Leave scripting to Javascript instead of inline <script>
- Use double quotes for attributes, two-space indentation, and omit optional closing tags where valid.

### CSS

- Use CSS grid or flexbox for layout 
- Use rem units for typography and spacing to respect user preferences, and CSS Grid/Flexbox for layout.
- Define custom properties (--var-name) at :root for colors, spacing, and typography to maintain consistency.
- Follow lowercase class names with hyphens (e.g., .btn-primary), avoiding camelCase or underscores.
- Utilize class selectors over IDs, keep specificity low
- Avoid @import; use link tags for CSS and modern media query syntax (e.g., @media (width >= 48rem)).

### Vanilla JavaScript

- Use let and const instead of var for block-scoped variables.
- Leverage modern web primitives (e.g., Element.startViewTransition(), IntersectionObserver) instead of libraries for common tasks.
- Handle security (XSS, CSP) manually if no framework is present, as vanilla JS lacks built-in protections.
