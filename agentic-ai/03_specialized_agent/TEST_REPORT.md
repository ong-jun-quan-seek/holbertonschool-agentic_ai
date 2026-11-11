# 1. Generation and Standardization (Application of the Skill)

## Generated file 

name: `cart_calculator.test.js`
path: `agentic-ai/03_specialized_agent/tests/cart_calculator.test.js`

## Tests executed

Total test: 17

## Final result of `npm test`

```
 PASS  tests/cart_calculator.test.js
  calculateTotal
    when the cart is invalid or empty
      ✓ should_return_zero_when_cart_is_empty (1 ms)
      ✓ should_return_zero_when_items_is_not_an_array
      ✓ should_return_zero_when_items_is_undefined (1 ms)
    when computing line items and subtotals
      ✓ should_apply_default_tax_rate_when_tax_rate_is_omitted
      ✓ should_apply_default_discount_when_discount_is_omitted
      ✓ should_sum_multiple_line_items_before_tax
      ✓ should_treat_missing_quantity_as_one
      ✓ should_treat_missing_price_as_zero
      ✓ should_clamp_negative_prices_to_zero
      ✓ should_clamp_negative_quantities_to_zero
      ✓ should_treat_zero_quantity_as_one_due_to_falsy_fallback (1 ms)
    when applying tax
      ✓ should_return_subtotal_unchanged_when_tax_rate_is_zero
      ✓ should_apply_custom_tax_rate_to_discounted_subtotal
    when applying discounts
      ✓ should_subtract_fixed_discount_before_tax
      ✓ should_not_allow_subtotal_to_go_below_zero_after_discount
    when rounding the total in euros
      ✓ should_round_total_to_two_decimal_places
      ✓ should_return_whole_number_totals_without_extra_decimals

Test Suites: 1 passed, 1 total
Tests:       17 passed, 17 total
Snapshots:   0 total
Time:        0.121 s, estimated 1 s
Ran all test suites.
```

## Whether the Agent respected the prohibition against modifying the `/src` directory.

Yes, agent did not modify anything in `/src` directory