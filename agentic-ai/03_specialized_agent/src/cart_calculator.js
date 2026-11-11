/**
 * Calculates the total for an e-commerce shopping cart, including taxes and discounts.
 * @param {Array} items - List of items [{ price: 10, quantity: 2 }]
 * @param {Number} taxRate - Tax rate (e.g., 0.20 for 20%)
 * @param {Number} discount - Fixed discount amount in euros
 * @returns {Number} Total including tax, rounded to 2 decimal places
 */
function calculateTotal(items, taxRate = 0.20, discount = 0) {
    if (!Array.isArray(items) || items.length === 0) {
        return 0;
    }

    // Subtotal excl. tax
    let subTotal = items.reduce((total, item) => {
        const itemPrice = Math.max(0, item.price || 0);
        const itemQty = Math.max(0, item.quantity || 1);
        return total + (itemPrice * itemQty);
    }, 0);

    // Application of discounts and taxes
    subTotal = Math.max(0, subTotal - discount);
    const totalTTC = subTotal * (1 + taxRate);

    return Math.round(totalTTC * 100) / 100;
}

module.exports = { calculateTotal };