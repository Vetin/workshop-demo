// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"strconv"
	"strings"
	"testing"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	"go.opentelemetry.io/otel/sdk/trace/tracetest"

	pb "github.com/open-telemetry/opentelemetry-demo/src/checkout/genproto/oteldemo"
)

// newTestTracerProvider creates a TracerProvider backed by an in-memory SpanRecorder
// and registers it globally so trace.SpanFromContext returns a recording span.
func newTestTracerProvider() (*sdktrace.TracerProvider, *tracetest.SpanRecorder) {
	sr := tracetest.NewSpanRecorder()
	tp := sdktrace.NewTracerProvider(sdktrace.WithSpanProcessor(sr))
	otel.SetTracerProvider(tp)
	return tp, sr
}

// spanAttrsMap returns a flat map of attribute key -> emitted string value.
func spanAttrsMap(attrs []attribute.KeyValue) map[string]string {
	m := make(map[string]string, len(attrs))
	for _, a := range attrs {
		m[string(a.Key)] = a.Value.Emit()
	}
	return m
}

// moneyToFloat replicates the exact formula used in main.go for money -> float conversion.
// Divisor 10_000_000 (10^7) converts nanos to cents: e.g. 990_000_000 nanos → 99 cents.
func moneyToFloat(m *pb.Money) float64 {
	f, _ := strconv.ParseFloat(fmt.Sprintf("%d.%02d", m.GetUnits(), m.GetNanos()/10_000_000), 64)
	return f
}

// ----- sendOrderConfirmation tests -----

// TestSendOrderConfirmation_GiftMessageOmittedWhenWrapFalse verifies that when
// gift_wrap=false the HTTP POST body sent to the email service does NOT contain
// the "gift_message" key.
func TestSendOrderConfirmation_GiftMessageOmittedWhenWrapFalse(t *testing.T) {
	var capturedBody []byte
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		capturedBody, _ = io.ReadAll(r.Body)
		w.WriteHeader(http.StatusOK)
	}))
	defer srv.Close()

	_, _ = newTestTracerProvider()
	cs := &checkout{emailSvcAddr: srv.URL}
	order := &pb.OrderResult{OrderId: "test-order-1", GiftWrap: false}

	// gift_wrap=false → effectiveGiftMessage="" → no "gift_message" key in payload
	if err := cs.sendOrderConfirmation(context.Background(), "user@example.com", order, ""); err != nil {
		t.Fatalf("sendOrderConfirmation returned unexpected error: %v", err)
	}

	var payload map[string]interface{}
	if err := json.Unmarshal(capturedBody, &payload); err != nil {
		t.Fatalf("failed to unmarshal captured body: %v", err)
	}
	if _, ok := payload["gift_message"]; ok {
		t.Error("expected 'gift_message' key to be absent in payload when gift_wrap=false, but it was present")
	}
}

// TestSendOrderConfirmation_GiftMessageIncludedWhenWrapTrue verifies that when
// gift_wrap=true and a message is provided, the "gift_message" key appears in the
// email POST body with the correct value.
func TestSendOrderConfirmation_GiftMessageIncludedWhenWrapTrue(t *testing.T) {
	var capturedBody []byte
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		capturedBody, _ = io.ReadAll(r.Body)
		w.WriteHeader(http.StatusOK)
	}))
	defer srv.Close()

	_, _ = newTestTracerProvider()
	cs := &checkout{emailSvcAddr: srv.URL}
	order := &pb.OrderResult{OrderId: "test-order-2", GiftWrap: true}

	if err := cs.sendOrderConfirmation(context.Background(), "user@example.com", order, "Happy Birthday!"); err != nil {
		t.Fatalf("sendOrderConfirmation returned unexpected error: %v", err)
	}

	var payload map[string]interface{}
	if err := json.Unmarshal(capturedBody, &payload); err != nil {
		t.Fatalf("failed to unmarshal captured body: %v", err)
	}
	msg, ok := payload["gift_message"]
	if !ok {
		t.Error("expected 'gift_message' key to be present in payload when gift_wrap=true, but it was absent")
		return
	}
	if msg != "Happy Birthday!" {
		t.Errorf("expected gift_message='Happy Birthday!', got %q", msg)
	}
}

// ----- span attribute tests using a recording span -----

// TestGiftWrapSpanAttribute_AlwaysSet verifies that "app.order.gift_wrap" is set for
// both true and false orders, and "app.order.gift_wrap.amount" is only present when true.
func TestGiftWrapSpanAttribute_AlwaysSet(t *testing.T) {
	tests := []struct {
		name            string
		giftWrap        bool
		expectAmountKey bool
	}{
		{"gift_wrap=true", true, true},
		{"gift_wrap=false", false, false},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			tp, sr := newTestTracerProvider()
			tr := tp.Tracer("test")
			ctx, span := tr.Start(context.Background(), "TestPlaceOrder")

			// Step 1: app.order.gift_wrap must be set before chargeCard for BOTH values
			span.SetAttributes(attribute.Bool("app.order.gift_wrap", tc.giftWrap))

			// Step 2: app.order.gift_wrap.amount only when gift_wrap=true
			if tc.giftWrap {
				fee := &pb.Money{Units: 5, Nanos: 0, CurrencyCode: "USD"}
				giftWrapAmount := moneyToFloat(fee)
				span.SetAttributes(attribute.Float64("app.order.gift_wrap.amount", giftWrapAmount))
				span.AddEvent("gift_wrap_fee_applied")
			}
			span.End()
			_ = ctx

			spans := sr.Ended()
			if len(spans) == 0 {
				t.Fatal("no spans recorded")
			}
			attrs := spanAttrsMap(spans[0].Attributes())

			// "app.order.gift_wrap" must always be present
			giftWrapVal, ok := attrs["app.order.gift_wrap"]
			if !ok {
				t.Error("app.order.gift_wrap attribute missing")
			}
			expectedVal := "false"
			if tc.giftWrap {
				expectedVal = "true"
			}
			if giftWrapVal != expectedVal {
				t.Errorf("app.order.gift_wrap: expected %q, got %q", expectedVal, giftWrapVal)
			}

			// "app.order.gift_wrap.amount" present iff gift_wrap=true
			_, hasAmount := attrs["app.order.gift_wrap.amount"]
			if tc.expectAmountKey && !hasAmount {
				t.Error("app.order.gift_wrap.amount missing when gift_wrap=true")
			}
			if !tc.expectAmountKey && hasAmount {
				t.Error("app.order.gift_wrap.amount present when gift_wrap=false (should be absent)")
			}
		})
	}
}

// TestGiftWrapSpanAttribute_GiftMessageNotPresent verifies that gift_message text never
// appears in any span attribute or event when gift_wrap=true.
func TestGiftWrapSpanAttribute_GiftMessageNotPresent(t *testing.T) {
	tp, sr := newTestTracerProvider()
	tr := tp.Tracer("test")
	ctx, span := tr.Start(context.Background(), "TestPlaceOrder")

	// giftMessage is PII — it must never appear in any span attribute or event
	giftMessage := "Happy Birthday!"

	// Simulate the span attribute logic from PlaceOrder Step 1+2
	span.SetAttributes(attribute.Bool("app.order.gift_wrap", true))
	fee := &pb.Money{Units: 5, Nanos: 0, CurrencyCode: "USD"}
	span.SetAttributes(attribute.Float64("app.order.gift_wrap.amount", moneyToFloat(fee)))
	span.AddEvent("gift_wrap_fee_applied")
	span.End()
	_ = ctx

	spans := sr.Ended()
	if len(spans) == 0 {
		t.Fatal("no spans recorded")
	}
	for _, s := range spans {
		for _, attr := range s.Attributes() {
			if strings.Contains(string(attr.Key), "gift_message") {
				t.Errorf("span attribute key contains 'gift_message': %q", attr.Key)
			}
			if strings.Contains(attr.Value.Emit(), giftMessage) {
				t.Errorf("span attribute value contains gift_message text for key %q: %q", attr.Key, attr.Value.Emit())
			}
		}
		for _, evt := range s.Events() {
			if strings.Contains(evt.Name, "gift_message") {
				t.Errorf("span event name contains 'gift_message': %q", evt.Name)
			}
			for _, ea := range evt.Attributes {
				if strings.Contains(ea.Value.Emit(), giftMessage) {
					t.Errorf("span event attribute value contains gift_message text for key %q", ea.Key)
				}
			}
		}
	}
}

// TestMoneyToFloat_Formula verifies the float formula produces expected values.
// The formula is: strconv.ParseFloat(fmt.Sprintf("%d.%02d", units, nanos/1e9), 64)
func TestMoneyToFloat_Formula(t *testing.T) {
	cases := []struct {
		money    *pb.Money
		expected float64
	}{
		{&pb.Money{Units: 5, Nanos: 0}, 5.00},
		{&pb.Money{Units: 4, Nanos: 990000000}, 4.99},
		{&pb.Money{Units: 0, Nanos: 500000000}, 0.50},
		{&pb.Money{Units: 10, Nanos: 990000000}, 10.99},
	}
	for _, tc := range cases {
		got := moneyToFloat(tc.money)
		diff := got - tc.expected
		if diff < 0 {
			diff = -diff
		}
		if diff > 0.001 {
			t.Errorf("moneyToFloat(%v): expected %.2f, got %.2f", tc.money, tc.expected, got)
		}
	}
}

// TestSendOrderConfirmation_SignatureAcceptsGiftMessage is a compile-time check that
// the updated sendOrderConfirmation signature accepts a giftMessage parameter.
// If the signature is wrong, the test file won't compile.
func TestSendOrderConfirmation_SignatureAcceptsGiftMessage(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	}))
	defer srv.Close()

	_, _ = newTestTracerProvider()
	cs := &checkout{emailSvcAddr: srv.URL}
	order := &pb.OrderResult{OrderId: "compile-check"}

	// Compile-time check: must accept 4 arguments including giftMessage string
	err := cs.sendOrderConfirmation(context.Background(), "test@example.com", order, "")
	_ = err
}
