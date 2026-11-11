const { calculateTotal } = require('../src/cart_calculator');

describe('calculateTotal', () => {
  describe('when the cart is invalid or empty', () => {
    it('should_return_zero_when_cart_is_empty', () => {
      // Arrange
      const items = [];

      // Act
      const total = calculateTotal(items);

      // Assert
      expect(total).toBe(0);
    });

    it('should_return_zero_when_items_is_not_an_array', () => {
      // Arrange
      const items = null;

      // Act
      const total = calculateTotal(items);

      // Assert
      expect(total).toBe(0);
    });

    it('should_return_zero_when_items_is_undefined', () => {
      // Arrange
      const items = undefined;

      // Act
      const total = calculateTotal(items);

      // Assert
      expect(total).toBe(0);
    });
  });

  describe('when computing line items and subtotals', () => {
    it('should_apply_default_tax_rate_when_tax_rate_is_omitted', () => {
      // Arrange
      const items = [{ price: 10, quantity: 2 }];

      // Act
      const total = calculateTotal(items);

      // Assert
      expect(total).toBe(24);
    });

    it('should_apply_default_discount_when_discount_is_omitted', () => {
      // Arrange
      const items = [{ price: 50, quantity: 1 }];
      const taxRate = 0;

      // Act
      const total = calculateTotal(items, taxRate);

      // Assert
      expect(total).toBe(50);
    });

    it('should_sum_multiple_line_items_before_tax', () => {
      // Arrange
      const items = [
        { price: 10, quantity: 2 },
        { price: 5, quantity: 4 },
      ];
      const taxRate = 0;

      // Act
      const total = calculateTotal(items, taxRate);

      // Assert
      expect(total).toBe(40);
    });

    it('should_treat_missing_quantity_as_one', () => {
      // Arrange
      const items = [{ price: 12 }];
      const taxRate = 0;

      // Act
      const total = calculateTotal(items, taxRate);

      // Assert
      expect(total).toBe(12);
    });

    it('should_treat_missing_price_as_zero', () => {
      // Arrange
      const items = [{ quantity: 3 }];
      const taxRate = 0;

      // Act
      const total = calculateTotal(items, taxRate);

      // Assert
      expect(total).toBe(0);
    });

    it('should_clamp_negative_prices_to_zero', () => {
      // Arrange
      const items = [{ price: -15, quantity: 2 }];
      const taxRate = 0;

      // Act
      const total = calculateTotal(items, taxRate);

      // Assert
      expect(total).toBe(0);
    });

    it('should_clamp_negative_quantities_to_zero', () => {
      // Arrange
      const items = [{ price: 10, quantity: -2 }];
      const taxRate = 0;

      // Act
      const total = calculateTotal(items, taxRate);

      // Assert
      expect(total).toBe(0);
    });

    it('should_treat_zero_quantity_as_one_due_to_falsy_fallback', () => {
      // Arrange
      const items = [{ price: 8, quantity: 0 }];
      const taxRate = 0;

      // Act
      const total = calculateTotal(items, taxRate);

      // Assert
      expect(total).toBe(8);
    });
  });

  describe('when applying tax', () => {
    it('should_return_subtotal_unchanged_when_tax_rate_is_zero', () => {
      // Arrange
      const items = [{ price: 25, quantity: 2 }];
      const taxRate = 0;

      // Act
      const total = calculateTotal(items, taxRate);

      // Assert
      expect(total).toBe(50);
    });

    it('should_apply_custom_tax_rate_to_discounted_subtotal', () => {
      // Arrange
      const items = [{ price: 100, quantity: 1 }];
      const taxRate = 0.1;
      const discount = 20;

      // Act
      const total = calculateTotal(items, taxRate, discount);

      // Assert
      expect(total).toBe(88);
    });
  });

  describe('when applying discounts', () => {
    it('should_subtract_fixed_discount_before_tax', () => {
      // Arrange
      const items = [{ price: 10, quantity: 2 }];
      const taxRate = 0.2;
      const discount = 5;

      // Act
      const total = calculateTotal(items, taxRate, discount);

      // Assert
      expect(total).toBe(18);
    });

    it('should_not_allow_subtotal_to_go_below_zero_after_discount', () => {
      // Arrange
      const items = [{ price: 10, quantity: 1 }];
      const taxRate = 0.2;
      const discount = 50;

      // Act
      const total = calculateTotal(items, taxRate, discount);

      // Assert
      expect(total).toBe(0);
    });
  });

  describe('when rounding the total in euros', () => {
    it('should_round_total_to_two_decimal_places', () => {
      // Arrange
      const items = [{ price: 0.33, quantity: 3 }];
      const taxRate = 0.2;

      // Act
      const total = calculateTotal(items, taxRate);

      // Assert
      expect(total).toBe(1.19);
    });

    it('should_return_whole_number_totals_without_extra_decimals', () => {
      // Arrange
      const items = [{ price: 10, quantity: 1 }];
      const taxRate = 0.2;

      // Act
      const total = calculateTotal(items, taxRate);

      // Assert
      expect(total).toBe(12);
    });
  });
});
