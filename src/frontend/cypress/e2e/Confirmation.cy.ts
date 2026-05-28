// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0

// Minimal order fixture shared by tests
const baseOrder = {
  orderId: 'test-order-123',
  items: [],
  shippingAddress: {
    streetAddress: '1600 Amphitheatre Pkwy',
    city: 'Mountain View',
    state: 'CA',
    country: 'United States',
    zipCode: '94043',
  },
  shippingCost: { units: 10, nanos: 0, currencyCode: 'USD' },
  giftWrap: false,
  giftWrapCost: undefined,
};

describe('Confirmation Page — Gift Wrap Display', () => {
  it('shows gift wrap fee row when order included gift wrap', () => {
    const order = { ...baseOrder, giftWrap: true, giftWrapCost: { units: 5, nanos: 0, currencyCode: 'USD' } };
    cy.visit(`/cart/checkout/test-order-123?order=${encodeURIComponent(JSON.stringify(order))}`);
    cy.contains('Gift Wrap:').should('be.visible');
    // Verify total = shipping ($10) + gift wrap ($5) = $15 USD
    // ProductPrice renders as "$ 15.00" (currency symbol + space + amount)
    cy.contains('$ 15.00').should('be.visible');
  });

  it('does not show gift wrap fee row for standard order', () => {
    const order = { ...baseOrder, giftWrap: false };
    cy.visit(`/cart/checkout/test-order-123?order=${encodeURIComponent(JSON.stringify(order))}`);
    cy.contains('Gift Wrap:').should('not.exist');
  });
});
