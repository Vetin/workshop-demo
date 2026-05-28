// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0

import { getElementByField } from '../../utils/Cypress';
import { CypressFields } from '../../utils/enums/CypressFields';

describe('Checkout Flow', () => {
  beforeEach(() => {
    cy.intercept('POST', '/api/cart*').as('addToCart');
    cy.intercept('GET', '/api/cart*').as('getCart');
    cy.intercept('POST', '/api/checkout*').as('placeOrder');
    cy.visit('/');
  });

  it('should create an order with two items', () => {
    getElementByField(CypressFields.ProductCard).first().click();
    getElementByField(CypressFields.ProductAddToCart).click();

    cy.wait('@addToCart');
    cy.wait('@getCart', { timeout: 10000 });
    cy.wait(2000);

    cy.location('href').should('match', /\/cart$/);
    getElementByField(CypressFields.CartItemCount).should('contain', '1');

    cy.visit('/');

    getElementByField(CypressFields.ProductCard).last().click();
    getElementByField(CypressFields.ProductAddToCart).click();

    cy.wait('@addToCart');
    cy.wait('@getCart', { timeout: 10000 });
    cy.wait(2000);

    cy.location('href').should('match', /\/cart$/);
    getElementByField(CypressFields.CartItemCount).should('contain', '2');

    getElementByField(CypressFields.CartIcon).click({ force: true });
    getElementByField(CypressFields.CartGoToShopping).click();

    cy.location('href').should('match', /\/cart$/);

    getElementByField(CypressFields.CheckoutPlaceOrder).click();

    cy.wait('@placeOrder');

    cy.location('href').should('match', /\/checkout/);
    getElementByField(CypressFields.CheckoutItem).should('have.length', 2);
  });

  it('shows gift wrap checkbox on checkout page', () => {
    getElementByField(CypressFields.ProductCard).first().click();
    getElementByField(CypressFields.ProductAddToCart).click();
    cy.wait('@addToCart');
    cy.wait('@getCart', { timeout: 10000 });
    cy.wait(2000);
    cy.location('href').should('match', /\/cart$/);
    getElementByField(CypressFields.GiftWrapCheckbox).should('exist');
  });

  it('checking gift wrap shows gift message textarea', () => {
    getElementByField(CypressFields.ProductCard).first().click();
    getElementByField(CypressFields.ProductAddToCart).click();
    cy.wait('@addToCart');
    cy.wait('@getCart', { timeout: 10000 });
    cy.wait(2000);
    cy.location('href').should('match', /\/cart$/);
    getElementByField(CypressFields.GiftMessageTextarea).should('not.exist');
    getElementByField(CypressFields.GiftWrapCheckbox).check();
    getElementByField(CypressFields.GiftMessageTextarea).should('be.visible');
  });

  it('unchecking gift wrap hides textarea and clears message', () => {
    getElementByField(CypressFields.ProductCard).first().click();
    getElementByField(CypressFields.ProductAddToCart).click();
    cy.wait('@addToCart');
    cy.wait('@getCart', { timeout: 10000 });
    cy.wait(2000);
    cy.location('href').should('match', /\/cart$/);
    getElementByField(CypressFields.GiftWrapCheckbox).check();
    getElementByField(CypressFields.GiftMessageTextarea).type('Hello');
    getElementByField(CypressFields.GiftWrapCheckbox).uncheck();
    getElementByField(CypressFields.GiftMessageTextarea).should('not.exist');
  });

  it('gift wrap fee row appears in cart summary when gift wrap is checked', () => {
    getElementByField(CypressFields.ProductCard).first().click();
    getElementByField(CypressFields.ProductAddToCart).click();
    cy.wait('@addToCart');
    cy.wait('@getCart', { timeout: 10000 });
    cy.wait(2000);
    cy.location('href').should('match', /\/cart$/);
    cy.contains('Gift Wrap').should('not.exist');
    getElementByField(CypressFields.GiftWrapCheckbox).check();
    cy.contains('Gift Wrap').should('be.visible');
    getElementByField(CypressFields.GiftWrapCheckbox).uncheck();
    cy.contains('Gift Wrap').should('not.exist');
  });

  it('gift wrap fields included in checkout POST body', () => {
    getElementByField(CypressFields.ProductCard).first().click();
    getElementByField(CypressFields.ProductAddToCart).click();

    cy.wait('@addToCart');
    cy.wait('@getCart', { timeout: 10000 });
    cy.wait(2000);

    cy.location('href').should('match', /\/cart$/);
    getElementByField(CypressFields.GiftWrapCheckbox).check();
    getElementByField(CypressFields.GiftMessageTextarea).type('test gift message');
    getElementByField(CypressFields.CheckoutPlaceOrder).click();

    cy.wait('@placeOrder').then(({ request }) => {
      expect(request.body).to.have.property('giftWrap', true);
      expect(request.body).to.have.property('giftMessage').and.be.a('string').and.not.be.empty;
    });
  });
});

export {};
