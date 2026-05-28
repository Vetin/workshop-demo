# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0
#
# Tests for email_server.rb gift message rendering.
#
# Run with the portable Ruby that has the required gems installed:
#
#   PORTABLE_RUBY=/opt/homebrew/Library/Homebrew/vendor/portable-ruby/3.4.8
#   PATH="$PORTABLE_RUBY/bin:$PATH" bundle exec ruby email_server_test.rb
#
# Or run directly (if gems are on the load path):
#   ruby -I<gem_paths...> email_server_test.rb

require 'minitest/autorun'
require 'rack/test'

# ---------------------------------------------------------------------------
# Patch OpenTelemetry::SDK.configure to be a no-op so the test process
# does not attempt to connect to an OTLP collector.
# This must run before email_server.rb is required.
# ---------------------------------------------------------------------------
require 'opentelemetry/sdk'

# Patch SDK configure to be a no-op (no OTLP collector in test env)
module OpenTelemetry
  module SDK
    def self.configure
      # no-op: skip real SDK initialization in tests
    end
  end
end

# Load metrics SDK so the MeterProvider class is defined
require 'opentelemetry-metrics-sdk'

# Patch SDK MeterProvider to stub add_metric_reader so it doesn't fail
# when the proxy meter provider is used instead of a real SDK meter provider
module OpenTelemetry
  module SDK
    module Metrics
      class MeterProvider
        def add_metric_reader(reader)
          # no-op in tests
        end
      end
    end
  end
end

# Stub the global meter_provider to return a no-op provider
module OpenTelemetry
  @_test_meter_provider = nil

  def self.meter_provider
    @_test_meter_provider ||= Object.new.tap do |mp|
      def mp.add_metric_reader(*) = nil
      def mp.meter(*)
        Object.new.tap do |m|
          def m.create_counter(*) = Object.new.tap { |c| def c.add(*) = nil }
        end
      end
    end
  end
end

# Also prevent the metrics exporter from trying to connect
require 'opentelemetry-exporter-otlp-metrics'
module OpenTelemetry
  module Exporter
    module OTLP
      module Metrics
        class MetricsExporter
          def initialize(**kwargs)
            # no-op: don't connect to collector in tests
          end
        end
      end
    end
  end
end

# Patch OpenFeature SDK to skip flagd connection
require 'open_feature/sdk'
require 'openfeature/flagd/provider'

module OpenFeature
  module SDK
    def self.configure
      # no-op: skip real provider registration
    end

    def self.build_client
      # Return a stub client that returns safe defaults
      Object.new.tap do |c|
        def c.fetch_number_value(flag_key:, default_value:)
          default_value
        end
      end
    end
  end

  module Flagd
    module Provider
      def self.build_client
        # Return a stub that accepts configure block without connecting
        Object.new.tap do |obj|
          def obj.configure
            yield self if block_given?
          end

          def obj.host=(val); nil; end
          def obj.port=(val); nil; end
          def obj.tls=(val);  nil; end
        end
      end
    end
  end
end

# ---------------------------------------------------------------------------
# Pony stub — captures sent mail options for test assertions
# ---------------------------------------------------------------------------
require 'pony'
module Pony
  @last_mail = nil

  class << self
    alias_method :_original_mail, :mail

    def mail(opts = {})
      @last_mail = opts
      # Don't call original: no SMTP available in tests
    end

    def last_mail
      @last_mail
    end

    def reset!
      @last_mail = nil
    end
  end
end

# ---------------------------------------------------------------------------
# Mail::TestMailer stub — email_server.rb calls Mail::TestMailer.deliveries.clear
# The real mail gem defines this but we ensure it's available even if Pony's
# test mailer isn't initialized.
# ---------------------------------------------------------------------------
require 'mail'
unless defined?(Mail::TestMailer)
  module Mail
    module TestMailer
      @deliveries = []
      def self.deliveries
        @deliveries
      end
    end
  end
end

# ---------------------------------------------------------------------------
# Load the Sinatra application (after all stubs are in place)
# ---------------------------------------------------------------------------
ENV['EMAIL_PORT'] ||= '6060'

require_relative 'email_server'

# Disable Rack::Protection (host authorization, CSRF) for rack-test
Sinatra::Application.disable :protection
Sinatra::Application.set :host_authorization, { permitted_hosts: [] }
# Prevent Sinatra from showing detailed exception pages (which can echo rendered
# email body content containing PII like gift_message in development mode)
Sinatra::Application.set :show_exceptions, false

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
class EmailServerTest < Minitest::Test
  include Rack::Test::Methods

  def app
    Sinatra::Application
  end

  def setup
    Pony.reset!
  end

  # Build a minimal valid JSON payload for POST /send_order_confirmation.
  def order_payload(extra = {})
    payload = {
      email: "test@example.com",
      order: {
        order_id: "test-order-123",
        shipping_tracking_id: "TRACK001",
        shipping_cost: { units: 5, nanos: 0, currency_code: "USD" },
        shipping_address: {
          street_address_1: "123 Main St",
          street_address_2: "",
          city: "Springfield",
          country: "US",
          zip_code: "12345"
        },
        items: []
      }
    }
    payload.merge(extra)
  end

  def post_order(extra = {})
    post '/send_order_confirmation',
         order_payload(extra).to_json,
         'CONTENT_TYPE' => 'application/json'
  end

  # Returns the body of the rendered confirmation email (passed to Pony.mail)
  def last_email_body
    Pony.last_mail&.fetch(:body, "") || ""
  end

  # a. Gift message present — should appear in rendered email HTML
  def test_gift_message_rendered_when_present
    post_order(gift_message: "Happy Birthday!")
    assert_equal 200, last_response.status,
      "Expected 200 but got #{last_response.status}: #{last_response.body[0..200]}"
    assert_includes last_email_body, "Happy Birthday!",
      "Expected gift message text in rendered email HTML"
  end

  # b. No gift_message key — "Gift Message" section should be absent
  def test_no_gift_message_section_when_absent
    post_order  # no gift_message key
    assert_equal 200, last_response.status,
      "Expected 200 but got #{last_response.status}: #{last_response.body[0..200]}"
    refute_nil Pony.last_mail, "Expected Pony.mail to have been called — route may have crashed"
    refute_includes last_email_body, "Gift Message",
      "Expected no Gift Message section when key is absent"
  end

  # c. Empty string gift_message — "Gift Message" section should be absent
  def test_gift_message_section_empty_string
    post_order(gift_message: "")
    assert_equal 200, last_response.status,
      "Expected 200 but got #{last_response.status}: #{last_response.body[0..200]}"
    refute_nil Pony.last_mail, "Expected Pony.mail to have been called — route may have crashed"
    refute_includes last_email_body, "Gift Message",
      "Expected no Gift Message section when value is empty string"
  end

  # d. XSS in gift_message — must be HTML-escaped, not rendered raw
  def test_gift_message_xss_escaped
    post_order(gift_message: "<script>alert(1)</script>")
    assert_equal 200, last_response.status,
      "Expected 200 but got #{last_response.status}: #{last_response.body[0..200]}"
    assert_includes last_email_body, "&lt;script&gt;",
      "Expected XSS payload to be HTML-escaped in rendered email"
    refute_includes last_email_body, "<script>alert(1)</script>",
      "Expected raw <script> tag to NOT appear in rendered email"
  end

  # 3a. gift_message absent from payload — no gift_message key — must not crash
  def test_no_gift_message_key_handled_gracefully
    # gift_message key absent from top-level payload — data.gift_message returns nil from OpenStruct
    payload = order_payload  # no gift_message key at top level
    post '/send_order_confirmation', payload.to_json, 'CONTENT_TYPE' => 'application/json'
    assert_equal 200, last_response.status,
      "Expected 200 when gift_message absent from payload: #{last_response.body[0..200]}"
  end

  # 3b. Pony exception does not leak gift_message text in the HTTP error response
  def test_pony_exception_does_not_capture_gift_message
    gift_msg = "Secret Birthday Message"
    original_mail = Pony.method(:mail)
    begin
      # Arrange: make Pony raise a generic exception unrelated to gift_message
      Pony.define_singleton_method(:mail) do |opts|
        raise "SMTP connection refused"
      end
      # Act
      post '/send_order_confirmation',
           order_payload(gift_message: gift_msg).to_json,
           'CONTENT_TYPE' => 'application/json'
      # Assert: the gift message text must NOT appear in the HTTP response body.
      # Sinatra's error handler returns a generic error page; it must not echo back
      # PII from the request body.
      refute_includes last_response.body, gift_msg,
        "Gift message text must not appear in the HTTP error response body"
    ensure
      Pony.define_singleton_method(:mail, &original_mail)
    end
  end

  # 3c. JSON null gift_message (Ruby nil) — no Gift Message section rendered
  def test_gift_message_null_in_json
    # JSON null → Ruby nil → OpenStruct nil
    post '/send_order_confirmation',
         order_payload.merge(gift_message: nil).to_json,
         'CONTENT_TYPE' => 'application/json'
    assert_equal 200, last_response.status,
      "Expected 200 for null gift_message: #{last_response.body[0..200]}"
    refute_nil Pony.last_mail, "Expected Pony.mail to have been called"
    refute_includes last_email_body, "Gift Message",
      "Expected no Gift Message section when gift_message is null"
  end

  # 3e. gift_message text must not appear in span attribute values
  def test_gift_message_not_in_span_attributes
    gift_msg = "Surprise Gift Note"
    captured_attributes = {}

    # Capture span attribute calls by patching the current span
    original_current_span = OpenTelemetry::Trace.method(:current_span)
    spy_span = Object.new
    spy_span.define_singleton_method(:add_attributes) do |attrs|
      captured_attributes.merge!(attrs)
    end
    spy_span.define_singleton_method(:record_exception) { |*| }

    OpenTelemetry::Trace.define_singleton_method(:current_span) { spy_span }

    begin
      post_order(gift_message: gift_msg)
      # Verify no span attribute value contains the gift message text.
      # Note: the inner send_email span uses tracer.in_span and only sets
      # app.email.recipient (the email address, not gift_message) — verified by
      # code review. This test captures current_span attributes.
      captured_attributes.each do |key, value|
        refute_includes value.to_s, gift_msg,
          "Span attribute '#{key}' must not contain gift message text"
      end
    ensure
      OpenTelemetry::Trace.define_singleton_method(:current_span, &original_current_span)
    end
  end
end
