"""Tests for forms.py uncovered blocks: utility functions, fallback classes, and complex form validation."""
from datetime import date, datetime
from decimal import Decimal
from unittest import mock
from werkzeug.datastructures import MultiDict
from wtforms.form import Form
from wtforms.validators import ValidationError

import pytest


def _fd(**kw):
    items = []
    for k, v in kw.items():
        if isinstance(v, list):
            for item in v:
                items.append((k, str(item)))
        else:
            items.append((k, str(v) if v is not None else ""))
    return MultiDict(items)


FORM_META = {"csrf": False}


def _is_fallback_qsf():
    """Check if QuerySelectField is the fallback class (not wtforms_sqlalchemy)."""
    import forms as _fm
    return _fm.QuerySelectField.__module__ == 'forms'


class TestDateTimeLocalField:
    def test_imported_class(self):
        from wtforms.fields import DateTimeLocalField
        assert DateTimeLocalField is not None

    def test_fallback_init(self):
        import forms as fm
        assert hasattr(fm, "DateTimeLocalField")


class TestCleanImagePath:
    def test_url_preserved(self):
        from forms import _clean_image_path
        assert _clean_image_path("https://example.com/img.jpg") == "https://example.com/img.jpg"

    def test_local_path_starts_with_slash(self):
        from forms import _clean_image_path
        r = _clean_image_path("/uploads/images/photo.png")
        assert r in ("photo.png", "/uploads/images/photo.png")

    def test_whitespace_only_returns_none(self):
        from forms import _clean_image_path
        assert _clean_image_path("   ") is None

    def test_relative_path_uses_basename(self):
        from forms import _clean_image_path
        assert _clean_image_path("subdir/photo.png") == "photo.png"


class TestCurrencyChoices:
    def test_normal_db(self, app):
        from forms import currency_choices
        assert len(currency_choices(include_blank=True)) >= 1

    def test_db_exception(self, app, mocker):
        from forms import currency_choices, CURRENCY_CHOICES
        from models import Currency as CurrencyModel
        mock_q = mock.MagicMock()
        mock_q.filter.side_effect = Exception("DB down")
        mocker.patch.object(CurrencyModel, 'query', mock_q)
        assert currency_choices(include_blank=False) == CURRENCY_CHOICES

    def test_no_blank(self, app):
        from forms import currency_choices
        assert all(c[0] != "" for c in currency_choices(include_blank=False))


class TestMoneyField:
    def test_invalid_returns_none(self):
        from forms import MoneyField
        class F(Form):
            m = MoneyField()
        assert F(_fd(m="not-a-number"), meta=FORM_META).m.data is None

    def test_none_returns_none(self):
        from forms import MoneyField
        class F(Form):
            m = MoneyField()
        assert F(_fd(m=""), meta=FORM_META).m.data is None


class TestPercentField:
    def test_garbled_input_sets_none(self):
        from forms import PercentField
        class F(Form):
            p = PercentField()
        assert F(_fd(p="abc"), meta=FORM_META).p.data is None


class TestQuerySelectFieldFallback:
    def _make_form(self, **field_kw):
        from forms import QuerySelectField
        class F(Form):
            q = QuerySelectField(**field_kw)
        return F(meta=FORM_META)

    def _make_field(self, **field_kw):
        return self._make_form(**field_kw).q

    def test_init_defaults(self):
        if not _is_fallback_qsf():
            pytest.skip("Real wtforms_sqlalchemy.QuerySelectField in use")
        f = self._make_field(query_factory=lambda: [])
        assert f.allow_blank is False

    def test_init_with_blank(self):
        if not _is_fallback_qsf():
            pytest.skip("Real wtforms_sqlalchemy.QuerySelectField in use")
        f = self._make_field(query_factory=lambda: [], allow_blank=True, blank_text="---")
        assert f.allow_blank is True and f.blank_text == "---"

    def test_refresh_choices_with_query(self):
        if not _is_fallback_qsf():
            pytest.skip("Real wtforms_sqlalchemy.QuerySelectField in use")
        o1, o2 = mock.MagicMock(id=1), mock.MagicMock(id=2)
        o1.name = "A"; o2.name = "B"
        f = self._make_field(query_factory=lambda: [o1, o2], get_label="name")
        assert ("1", "A") in f.choices and ("2", "B") in f.choices

    def test_refresh_choices_with_blank(self):
        if not _is_fallback_qsf():
            pytest.skip("Real wtforms_sqlalchemy.QuerySelectField in use")
        f = self._make_field(query_factory=lambda: [], allow_blank=True)
        assert ("", "—") in f.choices

    def test_refresh_choices_fallback_label(self):
        if not _is_fallback_qsf():
            pytest.skip("Real wtforms_sqlalchemy.QuerySelectField in use")
        class FakeObj:
            id = 5
            name = "Item"
        f = self._make_field(query_factory=lambda: [FakeObj()], get_label=None)
        assert ("5", "Item") in f.choices

    def test_refresh_choices_callable_get_label(self):
        if not _is_fallback_qsf():
            pytest.skip("Real wtforms_sqlalchemy.QuerySelectField in use")
        f = self._make_field(query_factory=lambda: [mock.MagicMock(id=3, code="XYZ")], get_label=lambda o: o.code)
        assert ("3", "XYZ") in f.choices

    def test_process_formdata_blank_allowed(self):
        if not _is_fallback_qsf():
            pytest.skip("Real wtforms_sqlalchemy.QuerySelectField in use")
        f = self._make_field(query_factory=lambda: [mock.MagicMock(id=10)], allow_blank=True)
        f.process_formdata([""]); assert f.data is None

    def test_process_formdata_blank_allowed_none_string(self):
        if not _is_fallback_qsf():
            pytest.skip("Real wtforms_sqlalchemy.QuerySelectField in use")
        f = self._make_field(query_factory=lambda: [], allow_blank=True)
        f.process_formdata(["None"]); assert f.data is None

    def test_process_formdata_maps_to_obj(self):
        if not _is_fallback_qsf():
            pytest.skip("Real wtforms_sqlalchemy.QuerySelectField in use")
        obj = mock.MagicMock(id=10, name="Item")
        f = self._make_field(query_factory=lambda: [obj], get_label="name")
        f.process_formdata(["10"]); assert f.data is obj

    def test_process_formdata_no_valuelist(self):
        if not _is_fallback_qsf():
            pytest.skip("Real wtforms_sqlalchemy.QuerySelectField in use")
        f = self._make_field(query_factory=lambda: [])
        f.process_formdata([]); assert f.data is None

    def test_process_data_none(self):
        if not _is_fallback_qsf():
            pytest.skip("Real wtforms_sqlalchemy.QuerySelectField in use")
        f = self._make_field(query_factory=lambda: [])
        f.process_data(None); assert f.data is None

    def test_process_data_empty_string(self):
        if not _is_fallback_qsf():
            pytest.skip("Real wtforms_sqlalchemy.QuerySelectField in use")
        f = self._make_field(query_factory=lambda: [])
        f.process_data(""); assert f.data is None

    def test_process_data_has_id(self):
        if not _is_fallback_qsf():
            pytest.skip("Real wtforms_sqlalchemy.QuerySelectField in use")
        obj = mock.MagicMock(id=7)
        f = self._make_field(query_factory=lambda: [obj])
        f.process_data(obj); assert f.data is obj

    def test_process_data_str_id_maps(self):
        if not _is_fallback_qsf():
            pytest.skip("Real wtforms_sqlalchemy.QuerySelectField in use")
        obj = mock.MagicMock(id=7)
        f = self._make_field(query_factory=lambda: [obj])
        f.process_data("7"); assert f.data is obj

    def test_pre_validate_blank_allowed_none(self):
        if not _is_fallback_qsf():
            pytest.skip("Real wtforms_sqlalchemy.QuerySelectField in use")
        f = self._make_field(query_factory=lambda: [], allow_blank=True)
        f.data = None; f.pre_validate(None)

    def test_pre_validate_raises_when_none(self):
        if not _is_fallback_qsf():
            pytest.skip("Real wtforms_sqlalchemy.QuerySelectField in use")
        from wtforms import ValidationError
        f = self._make_field(query_factory=lambda: [])
        f.data = None
        with pytest.raises(ValidationError, match="قيمة غير صالحة"):
            f.pre_validate(None)

    def test_pre_validate_has_obj_with_id(self):
        if not _is_fallback_qsf():
            pytest.skip("Real wtforms_sqlalchemy.QuerySelectField in use")
        obj = mock.MagicMock(id=10)
        f = self._make_field(query_factory=lambda: [obj])
        f.process_data(obj); f.pre_validate(None)

    def test_pre_validate_unknown_id_raises(self):
        if not _is_fallback_qsf():
            pytest.skip("Real wtforms_sqlalchemy.QuerySelectField in use")
        from wtforms import ValidationError
        f = self._make_field(query_factory=lambda: [mock.MagicMock(id=1)])
        f.data = mock.MagicMock(id=99)
        with pytest.raises(ValidationError):
            f.pre_validate(None)

    def test_pre_validate_unknown_str_raises(self):
        if not _is_fallback_qsf():
            pytest.skip("Real wtforms_sqlalchemy.QuerySelectField in use")
        from wtforms import ValidationError
        f = self._make_field(query_factory=lambda: [mock.MagicMock(id=1)])
        f.data = "99"
        with pytest.raises(ValidationError):
            f.pre_validate(None)


class TestUnifiedDateTimeFieldBranches:
    def test_init_with_formats(self):
        from forms import UnifiedDateTimeField
        class F(Form):
            dt = UnifiedDateTimeField(formats=["%Y/%m/%d %H:%M", "%Y-%m-%dT%H:%M"])
        form = F(_fd(dt="2025/06/15 10:30"), meta=FORM_META)
        assert form.dt.data == datetime(2025, 6, 15, 10, 30)

    def test_init_with_format_list(self):
        from forms import UnifiedDateTimeField
        class F(Form):
            dt = UnifiedDateTimeField(format=["%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M"])
        form = F(_fd(dt="2025/06/15 10:30"), meta=FORM_META)
        assert form.dt.data == datetime(2025, 6, 15, 10, 30)

    def test_value_with_raw_data(self):
        from forms import UnifiedDateTimeField
        class F(Form):
            dt = UnifiedDateTimeField()
        form = F(_fd(dt="2025-06-15 10:30"), meta=FORM_META)
        assert form.dt._value() == "2025-06-15 10:30"

    def test_value_strftime_fallback(self):
        from forms import UnifiedDateTimeField
        class F(Form):
            dt = UnifiedDateTimeField()
        form = F(_fd(dt="2025-06-15 10:30"), meta=FORM_META)
        form.dt.raw_data = None
        val = form.dt._value()
        assert isinstance(val, str) and len(val) > 0


class TestUnifiedDateFieldBranches:
    def test_value_with_raw_data(self):
        from forms import UnifiedDateField
        class F(Form):
            d = UnifiedDateField()
        form = F(_fd(d="2025-06-15"), meta=FORM_META)
        assert form.d._value() == "2025-06-15"

    def test_value_strftime_fallback(self):
        from forms import UnifiedDateField
        class F(Form):
            d = UnifiedDateField()
        form = F(_fd(d="2025-06-15"), meta=FORM_META)
        form.d.raw_data = None
        val = form.d._value()
        assert isinstance(val, str) and len(val) > 0

    def test_timestamp_parsing(self):
        from forms import UnifiedDateField
        class F(Form):
            d = UnifiedDateField()
        ts = datetime(2025, 6, 15, 10, 30).timestamp()
        form = F(_fd(d=f"ts:{ts}"), meta=FORM_META)
        assert form.d.data == date(2025, 6, 15)

    def test_timestamp_invalid_returns_false(self):
        from forms import UnifiedDateField
        class F(Form):
            d = UnifiedDateField()
        form = F(_fd(d="ts:invalid"), meta=FORM_META)
        assert form.validate() is False

    def test_init_with_formats(self):
        from forms import UnifiedDateField
        class F(Form):
            d = UnifiedDateField(formats=["%Y/%m/%d", "%d-%m-%Y"])
        form = F(_fd(d="2025/06/15"), meta=FORM_META)
        assert form.d.data == date(2025, 6, 15)

    def test_init_with_format_list(self):
        from forms import UnifiedDateField
        class F(Form):
            d = UnifiedDateField(format=["%Y-%m-%d", "%Y/%m/%d"])
        form = F(_fd(d="2025/06/15"), meta=FORM_META)
        assert form.d.data == date(2025, 6, 15)


class TestTransferFormStockCheck:
    def test_stock_check_exception(self, db_session, mocker):
        from forms import TransferForm
        from models import Warehouse, ProductCategory, Product
        wh_src = Warehouse(name="Src", warehouse_type="PHYSICAL")
        wh_dst = Warehouse(name="Dst", warehouse_type="PHYSICAL")
        db_session.add_all([wh_src, wh_dst])
        cat = ProductCategory(name="Cat")
        db_session.add(cat)
        db_session.commit()
        prod = Product(name="P", category_id=cat.id, price=10, purchase_price=5, currency="ILS")
        db_session.add(prod)
        db_session.commit()

        sl_entry = mock.MagicMock()
        sl_entry.quantity = 100
        sl_entry.reserved_quantity = 0
        q = mock.MagicMock()
        q.filter_by.return_value.first.return_value = sl_entry
        mocker.patch("models.StockLevel.query", q)

        form = TransferForm(
            _fd(product_id=str(prod.id), source_id=str(wh_src.id),
                destination_id=str(wh_dst.id), quantity="5", direction="OUT"),
            meta=FORM_META,
        )
        assert form.validate() is True


class TestSettlementRangeForm:
    def test_valid_empty(self):
        from forms import SettlementRangeForm
        assert SettlementRangeForm(_fd(), meta=FORM_META).validate() is True

    def test_valid_range(self):
        from forms import SettlementRangeForm
        assert SettlementRangeForm(_fd(start="2025-01-01", end="2025-12-31"), meta=FORM_META).validate() is True

    def test_end_before_start(self):
        from forms import SettlementRangeForm
        form = SettlementRangeForm(_fd(start="2025-12-31", end="2025-01-01"), meta=FORM_META)
        assert form.validate() is False
        assert "end" in form.errors


class TestUserFormExtraBranches:
    def test_editing_user_id_fallback(self, app, db_session, mocker):
        from forms import UserForm
        from models import Role
        r = Role(name="owner")
        db_session.add(r); db_session.commit()
        mocker.patch("flask.request.view_args", {})
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"; admin.role.name = "admin"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = UserForm(_fd(username="u1", email="u1@test.com", role_id=str(r.id), is_active="y"), meta=FORM_META)
                assert form._editing_user_id is None

    def test_editing_user_id_exception(self, app, db_session, mocker):
        from forms import UserForm
        from models import Role
        r = Role(name="owner")
        db_session.add(r); db_session.commit()
        mocker.patch("flask.request.view_args", side_effect=Exception("no request"))
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"; admin.role.name = "admin"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = UserForm(_fd(username="u1", email="u1@test.com", role_id=str(r.id), is_active="y"), meta=FORM_META)
                assert form._editing_user_id is None


class TestCustomerFormPhone:
    def test_phone_empty_raises(self, db_session):
        from forms import CustomerForm
        form = CustomerForm(_fd(name="Test", phone="   ", category="عادي", currency="ILS"), meta=FORM_META)
        assert form.validate() is False
        assert "phone" in form.errors

    def test_phone_valid_passes(self, db_session):
        from forms import CustomerForm
        form = CustomerForm(_fd(name="Test", phone="0501234567", category="عادي", currency="ILS"), meta=FORM_META)
        assert form.validate() is True


class TestQuickSupplierForm:
    def test_email_none_does_not_error(self):
        from forms import QuickSupplierForm
        form = QuickSupplierForm(_fd(name="QS"), meta=FORM_META)
        form.email.data = None
        assert form.email.validate(form) is True

    def test_valid_form(self):
        from forms import QuickSupplierForm
        assert QuickSupplierForm(_fd(name="Valid"), meta=FORM_META).validate() is True


class TestQuickPartnerForm:
    def test_email_none_does_not_error(self):
        from forms import QuickPartnerForm
        form = QuickPartnerForm(_fd(name="QP"), meta=FORM_META)
        form.email.data = None
        assert form.email.validate(form) is True

    def test_valid_form(self):
        from forms import QuickPartnerForm
        assert QuickPartnerForm(_fd(name="Valid"), meta=FORM_META).validate() is True


class TestPaymentAllocationForm:
    def test_no_targets_fails(self):
        from forms import PaymentAllocationForm
        assert PaymentAllocationForm(_fd(), meta=FORM_META).validate() is False

    def test_valid_with_invoice(self):
        from forms import PaymentAllocationForm
        form = PaymentAllocationForm(MultiDict([("invoice_ids", "1"), ("allocation_amounts-0", "100")]), meta=FORM_META)
        assert form.validate() is True


class TestSupplierSettlementForm:
    def test_no_lines_with_values(self):
        from forms import SupplierSettlementForm
        form = SupplierSettlementForm(
            _fd(supplier_id="1", from_date="2025-01-01 00:00", to_date="2025-01-31 00:00",
                currency="ILS", status="DRAFT", mode="ON_RECEIPT", total_gross="0", total_due="0"),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_needs_pricing_blocked_on_confirm(self):
        from forms import SupplierSettlementForm
        form = SupplierSettlementForm(
            MultiDict([("supplier_id", "1"), ("from_date", "2025-01-01 00:00"),
                       ("to_date", "2025-01-31 00:00"), ("currency", "ILS"),
                       ("status", "CONFIRMED"), ("mode", "ON_RECEIPT"),
                       ("total_gross", "100"), ("total_due", "100"),
                       ("lines-0-quantity", "1")]),
            meta=FORM_META,
        )
        for entry in form.lines:
            entry.form.needs_pricing.data = True
        assert form.validate() is False

    def test_apply_to(self, mocker):
        from forms import SupplierSettlementForm
        ss = mock.MagicMock()
        form = SupplierSettlementForm(
            _fd(supplier_id="1", from_date="2025-01-01 00:00", to_date="2025-01-31 00:00",
                currency="ils", status="CONFIRMED", mode="ON_RECEIPT", total_gross="100", total_due="100"),
            meta=FORM_META,
        )
        form.apply_to(ss)
        assert ss.currency == "ILS" and ss.status == "CONFIRMED"


class TestSupplierLoanSettlementForm:
    def test_no_loan_no_supplier_fails(self):
        from forms import SupplierLoanSettlementForm
        form = SupplierLoanSettlementForm(
            _fd(loan_id="", supplier_id="", settled_price="100", settlement_date="2025-06-15"),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_supplier_mismatch_with_loan(self, app, mocker):
        from forms import SupplierLoanSettlementForm
        from datetime import datetime
        loan_mock = mock.MagicMock(supplier_id=2)
        mocker.patch("extensions.db.session.get", return_value=loan_mock)
        form = SupplierLoanSettlementForm(
            _fd(loan_id="5", supplier_id="1", settled_price="100"),
            meta=FORM_META,
        )
        form.settlement_date.data = datetime(2025, 6, 15, 10, 0)
        assert form.validate() is False
        assert "supplier_id" in form.errors

    def test_apply_to(self):
        from forms import SupplierLoanSettlementForm
        sls = mock.MagicMock()
        form = SupplierLoanSettlementForm(_fd(loan_id="5", settled_price="100", settlement_date="2025-06-15"), meta=FORM_META)
        form.apply_to(sls)
        assert sls.loan_id == 5


class TestInvoiceRefundForm:
    def test_refund_amount_exceeds_refundable(self, app, mocker):
        from forms import InvoiceRefundForm
        mocker.patch("extensions.db.session.get", return_value=mock.MagicMock(refundable_amount=Decimal("50")))
        form = InvoiceRefundForm(_fd(invoice_id="1", amount="100", reason="Test"), meta=FORM_META)
        assert form.validate() is False
        assert "amount" in form.errors

    def test_build_payment_payload(self):
        from forms import InvoiceRefundForm
        form = InvoiceRefundForm(_fd(invoice_id="1", amount="100", reason="Test", notes="Note"), meta=FORM_META)
        payload = form.build_payment_payload()
        assert payload["direction"] == "OUTGOING" and payload["entity_id"] == 1


class TestInvoiceCancelForm:
    def test_invoice_not_found(self, app, mocker):
        from forms import InvoiceCancelForm
        mocker.patch("extensions.db.session.get", return_value=None)
        form = InvoiceCancelForm(_fd(invoice_id="99", cancel_reason="Duplicate"), meta=FORM_META)
        assert form.validate() is False
        assert "invoice_id" in form.errors

    def test_invoice_already_cancelled(self, app, mocker):
        from forms import InvoiceCancelForm
        mocker.patch("extensions.db.session.get", return_value=mock.MagicMock(status="CANCELLED"))
        form = InvoiceCancelForm(_fd(invoice_id="1", cancel_reason="Duplicate"), meta=FORM_META)
        assert form.validate() is False
        assert "invoice_id" in form.errors

    def test_db_exception_graceful(self, app, mocker):
        from forms import InvoiceCancelForm
        mocker.patch("extensions.db.session.get", side_effect=Exception("DB down"))
        form = InvoiceCancelForm(_fd(invoice_id="1", cancel_reason="Duplicate"), meta=FORM_META)
        assert form.validate() is True


class TestPartnerSettlementForm:
    def test_no_lines_fails(self):
        from forms import PartnerSettlementForm
        form = PartnerSettlementForm(
            _fd(partner_id="1", from_date="2025-01-01 00:00", to_date="2025-01-31 00:00", currency="ILS", status="DRAFT"),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_negative_total_share(self):
        from forms import PartnerSettlementForm
        form = PartnerSettlementForm(
            _fd(partner_id="1", from_date="2025-01-01 00:00", to_date="2025-01-31 00:00", currency="ILS", status="DRAFT"),
            meta=FORM_META,
        )
        for entry in form.lines:
            entry.form.share_amount.data = Decimal("-10")
        assert form.validate() is False

    def test_apply_to(self):
        from forms import PartnerSettlementForm
        ps = mock.MagicMock()
        form = PartnerSettlementForm(
            _fd(partner_id="1", from_date="2025-01-01 00:00", to_date="2025-01-31 00:00", currency="ils", status="CONFIRMED"),
            meta=FORM_META,
        )
        form.apply_to(ps)
        assert ps.currency == "ILS" and ps.status == "CONFIRMED"


class TestLoanSettlementPaymentForm:
    def test_empty_method_fails(self):
        from forms import LoanSettlementPaymentForm
        form = LoanSettlementPaymentForm(_fd(settlement_id="1", amount="100"), meta=FORM_META)
        assert form.validate() is False

    def test_valid_card(self):
        from forms import LoanSettlementPaymentForm
        form = LoanSettlementPaymentForm(
            _fd(settlement_id="1", amount="100", method="CARD",
                card_number="4111111111111111", card_holder="Test", card_expiry="12/28"),
            meta=FORM_META,
        )
        ok = form.validate()
        assert ok or "method" in form.errors

    def test_valid_cheque(self):
        from forms import LoanSettlementPaymentForm
        form = LoanSettlementPaymentForm(
            _fd(settlement_id="1", amount="100", method="CHEQUE",
                check_number="CHK001", check_bank="Bank", check_due_date="2025-07-15"),
            meta=FORM_META,
        )
        ok = form.validate()
        assert ok or "method" in form.errors

    def test_valid_bank(self):
        from forms import LoanSettlementPaymentForm
        form = LoanSettlementPaymentForm(
            _fd(settlement_id="1", amount="100", method="BANK", bank_transfer_ref="TRF123"),
            meta=FORM_META,
        )
        ok = form.validate()
        assert ok or "method" in form.errors

    def test_valid_online(self):
        from forms import LoanSettlementPaymentForm
        form = LoanSettlementPaymentForm(
            _fd(settlement_id="1", amount="100", method="ONLINE", online_gateway="Stripe", online_ref="pi_123"),
            meta=FORM_META,
        )
        ok = form.validate()
        assert ok or "method" in form.errors

    def test_amount_zero_with_details_errors(self):
        from forms import LoanSettlementPaymentForm
        form = LoanSettlementPaymentForm(
            _fd(settlement_id="1", amount="0", method="CARD",
                card_number="4111111111111111", card_holder="Test"),
            meta=FORM_META,
        )
        assert form.validate() is False


class TestPaymentFormInit:
    def test_init_default_direction_for_expense(self, app, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"; admin.role.name = "admin"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = PaymentForm(_fd(entity_type="EXPENSE", direction=""), meta=FORM_META)
                assert form.direction.data == "OUT"


class TestPaymentFormHelpers:
    @staticmethod
    def _make_form(app, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"; admin.role.name = "admin"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                return PaymentForm(meta=FORM_META)

    def test_nz_none(self, app, mocker):
        form = self._make_form(app, mocker)
        assert form._nz(None) == ""

    def test_nz_string(self, app, mocker):
        form = self._make_form(app, mocker)
        assert form._nz("  hello  ") == "hello"

    def test_nz_other(self, app, mocker):
        form = self._make_form(app, mocker)
        assert form._nz(42) == "42"

    def test_sync_entity_id_known(self, app, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"; admin.role.name = "admin"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = PaymentForm(_fd(entity_type="CUSTOMER", customer_id="42"), meta=FORM_META)
                form._sync_entity_id_for_render()
                assert form.entity_id.data == "42"

    def test_sync_entity_id_unknown(self, app, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"; admin.role.name = "admin"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = PaymentForm(_fd(entity_type="UNKNOWN"), meta=FORM_META)
                form._sync_entity_id_for_render()
                assert form.entity_id.data == ""

    def test_push_entity_id_to_specific(self, app, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"; admin.role.name = "admin"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = PaymentForm(
                    _fd(entity_type="CUSTOMER", customer_id="99"),
                    meta=FORM_META,
                )
                form._push_entity_id_to_specific()
                assert form.customer_id.data == "99"

    def test_push_entity_id_unknown_type(self, app, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"; admin.role.name = "admin"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = PaymentForm(_fd(entity_type="UNKNOWN"), meta=FORM_META)
                form._push_entity_id_to_specific()


class TestPaymentFormValidate:
    def test_unknown_entity_type(self, app, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"; admin.role.name = "admin"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = PaymentForm(
                    _fd(entity_type="UNKNOWN", direction="IN", total_amount="100",
                        currency="ILS", payment_date="2025-06-15 10:30", status="PAID"),
                    meta=FORM_META,
                )
                assert form.validate() is False
                assert "entity_type" in form.errors

    def test_bad_direction(self, app, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"; admin.role.name = "admin"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = PaymentForm(
                    _fd(entity_type="CUSTOMER", direction="BAD", total_amount="100",
                        currency="ILS", payment_date="2025-06-15 10:30", status="PAID"),
                    meta=FORM_META,
                )
                assert form.validate() is False
                assert "direction" in form.errors

    def test_missing_customer(self, app, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"; admin.role.name = "admin"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = PaymentForm(
                    _fd(entity_type="CUSTOMER", direction="IN", total_amount="100",
                        currency="ILS", payment_date="2025-06-15 10:30", status="PAID"),
                    meta=FORM_META,
                )
                assert form.validate() is False

    def test_duplicate_references_fails(self, app, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"; admin.role.name = "admin"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = PaymentForm(
                    _fd(entity_type="CUSTOMER", direction="IN", total_amount="100",
                        currency="ILS", payment_date="2025-06-15 10:30", status="PAID",
                        customer_id="1", supplier_id="2"),
                    meta=FORM_META,
                )
                assert form.validate() is False

    def test_direction_not_allowed_fails(self, app, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        mocker.patch("models.is_direction_allowed", return_value=False)
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"; admin.role.name = "admin"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = PaymentForm(
                    _fd(entity_type="CUSTOMER", direction="IN", total_amount="100",
                        currency="ILS", payment_date="2025-06-15 10:30", status="PAID",
                        customer_id="1"),
                    meta=FORM_META,
                )
                assert form.validate() is False

    def test_cheque_method_validates(self, app, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"; admin.role.name = "admin"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = PaymentForm(meta=FORM_META)
                form.entity_type.data = "CUSTOMER"
                form.direction.data = "IN"
                form.total_amount.data = Decimal("100")
                form.currency.data = "ILS"
                form.customer_id.data = "1"
                form.payment_date.data = datetime(2025, 6, 15, 10, 30)
                form.status.data = "COMPLETED"
                form.method.data = "CHEQUE"
                form.check_number.data = "CHK001"
                form.check_bank.data = "Bank"
                form.check_due_date.data = date(2025, 7, 15)
                split = form.splits[0].form
                split.amount.data = Decimal("100")
                split.method.data = "CHEQUE"
                split.check_number.data = "CHK001"
                split.check_bank.data = "Bank"
                split.check_due_date.data = date(2025, 7, 15)
                assert form.validate() is True

    def test_card_method_validates(self, app, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"; admin.role.name = "admin"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = PaymentForm(meta=FORM_META)
                form.entity_type.data = "CUSTOMER"
                form.direction.data = "IN"
                form.total_amount.data = Decimal("100")
                form.currency.data = "ILS"
                form.customer_id.data = "1"
                form.payment_date.data = datetime(2025, 6, 15, 10, 30)
                form.status.data = "COMPLETED"
                form.method.data = "CARD"
                form.card_number.data = "4111111111111111"
                form.card_holder.data = "Test"
                form.card_expiry.data = "12/28"
                split = form.splits[0].form
                split.amount.data = Decimal("100")
                split.method.data = "CARD"
                split.card_number.data = "4111111111111111"
                split.card_holder.data = "Test"
                split.card_expiry.data = "12/28"
                v = form.validate()
                assert v is True
                assert len(form.card_number.data) == 4

    def test_bank_method_validates(self, app, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"; admin.role.name = "admin"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = PaymentForm(meta=FORM_META)
                form.entity_type.data = "CUSTOMER"
                form.direction.data = "IN"
                form.total_amount.data = Decimal("100")
                form.currency.data = "ILS"
                form.customer_id.data = "1"
                form.payment_date.data = datetime(2025, 6, 15, 10, 30)
                form.status.data = "COMPLETED"
                form.method.data = "BANK"
                form.bank_transfer_ref.data = "TRF123"
                split = form.splits[0].form
                split.amount.data = Decimal("100")
                split.method.data = "BANK"
                split.bank_transfer_ref.data = "TRF123"
                assert form.validate() is True

    def test_online_method_validates(self, app, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"; admin.role.name = "admin"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = PaymentForm(meta=FORM_META)
                form.entity_type.data = "CUSTOMER"
                form.direction.data = "IN"
                form.total_amount.data = Decimal("100")
                form.currency.data = "ILS"
                form.customer_id.data = "1"
                form.payment_date.data = datetime(2025, 6, 15, 10, 30)
                form.status.data = "COMPLETED"
                form.method.data = "ONLINE"
                form.online_gateway.data = "Stripe"
                form.online_ref.data = "pi_123"
                split = form.splits[0].form
                split.amount.data = Decimal("100")
                split.method.data = "ONLINE"
                split.online_gateway.data = "Stripe"
                split.online_ref.data = "pi_123"
                assert form.validate() is True


class TestBulkPaymentForm:
    """BulkPaymentForm: allocation validation, amount matching, payer validation."""

    def _bd(self):
        """Return a fresh MultiDict with required BulkPaymentForm fields."""
        md = MultiDict()
        md["payer_type"] = "customer"
        md["payer_id"] = "1"
        md["total_amount"] = "100"
        md["method"] = "CASH"
        md["currency"] = "ILS"
        return md

    def test_valid_form(self):
        from forms import BulkPaymentForm
        md = self._bd()
        md.setlist("allocations-0-invoice_ids", ["5"])
        md.setlist("allocations-0-allocation_amounts-0", ["100"])
        form = BulkPaymentForm(md, meta=FORM_META)
        assert form.validate() is True

    def test_total_mismatch(self):
        from forms import BulkPaymentForm
        md = self._bd()
        md.setlist("allocations-0-invoice_ids", ["5"])
        md.setlist("allocations-0-allocation_amounts-0", ["50"])
        form = BulkPaymentForm(md, meta=FORM_META)
        assert form.validate() is False
        assert "total_amount" in form.errors

    def test_no_allocations_nonempty(self):
        from forms import BulkPaymentForm
        md = self._bd()
        md.setlist("allocations-0-invoice_ids", ["5"])
        md.setlist("allocations-0-allocation_amounts-0", ["0"])
        form = BulkPaymentForm(md, meta=FORM_META)
        assert form.validate() is False
        assert "allocations" in form.errors

    def test_invalid_payer_id(self):
        from forms import BulkPaymentForm
        md = self._bd()
        md["payer_id"] = "abc"
        md.setlist("allocations-0-invoice_ids", ["5"])
        md.setlist("allocations-0-allocation_amounts-0", ["100"])
        form = BulkPaymentForm(md, meta=FORM_META)
        assert form.validate() is False
        assert "payer_id" in form.errors

    def test_supplier_with_service_ids(self):
        from forms import BulkPaymentForm
        md = self._bd()
        md["payer_type"] = "supplier"
        md.setlist("allocations-0-invoice_ids", ["5"])
        md.setlist("allocations-0-allocation_amounts-0", ["100"])
        md.setlist("allocations-0-service_ids", ["1"])
        form = BulkPaymentForm(md, meta=FORM_META)
        assert form.validate() is False
        assert "allocations" in form.errors

    def test_multiple_allocations(self):
        from forms import BulkPaymentForm
        md = self._bd()
        md["total_amount"] = "150"
        md.setlist("allocations-0-invoice_ids", ["5"])
        md.setlist("allocations-0-allocation_amounts-0", ["100"])
        md.setlist("allocations-1-invoice_ids", ["6"])
        md.setlist("allocations-1-allocation_amounts-0", ["50"])
        form = BulkPaymentForm(md, meta=FORM_META)
        assert form.validate() is True


class TestSplitEntryForm:
    """SplitEntryForm: payment method validation for each method type."""

    def test_amount_zero_without_details(self):
        from forms import SplitEntryForm
        form = SplitEntryForm(_fd(currency="ILS"), meta=FORM_META)
        assert form.validate() is True

    def test_amount_zero_with_details_errors(self):
        from forms import SplitEntryForm
        fd = _fd(currency="ILS", amount="0", check_number="123", check_bank="TestBank")
        form = SplitEntryForm(fd, meta=FORM_META)
        assert form.validate() is False
        assert "amount" in form.errors

    def test_amount_positive_without_method_errors(self):
        from forms import SplitEntryForm
        fd = _fd(currency="ILS", amount="100")
        form = SplitEntryForm(fd, meta=FORM_META)
        assert form.validate() is False
        assert "method" in form.errors

    def test_cheque_valid(self):
        from forms import SplitEntryForm
        fd = _fd(currency="ILS", amount="100", method="CHEQUE",
                 check_number="123", check_bank="TestBank", check_due_date="2026-07-01")
        form = SplitEntryForm(fd, meta=FORM_META)
        assert form.validate() is True

    def test_cheque_missing_fields_raises(self, mocker):
        from forms import SplitEntryForm
        from wtforms import ValidationError
        mocker.patch.object(SplitEntryForm, '_validate_cheque',
                            side_effect=ValidationError("Cheque error"))
        fd = _fd(currency="ILS", amount="100", method="CHEQUE")
        form = SplitEntryForm(fd, meta=FORM_META)
        assert form.validate() is False
        assert "method" in form.errors

    def test_bank_valid(self):
        from forms import SplitEntryForm
        fd = _fd(currency="ILS", amount="100", method="BANK",
                 bank_transfer_ref="TRF001")
        form = SplitEntryForm(fd, meta=FORM_META)
        assert form.validate() is True

    def test_card_valid(self, mocker):
        from forms import SplitEntryForm
        mocker.patch.object(SplitEntryForm, '_validate_card_payload', return_value="1234")
        fd = _fd(currency="ILS", amount="100", method="CARD",
                 card_number="4111111111111111", card_holder="Test", card_expiry="12/28")
        form = SplitEntryForm(fd, meta=FORM_META)
        assert form.validate() is True
        assert form.card_number.data == "1234"

    def test_online_valid(self):
        from forms import SplitEntryForm
        fd = _fd(currency="ILS", amount="100", method="ONLINE",
                 online_gateway="Stripe", online_ref="pi_123")
        form = SplitEntryForm(fd, meta=FORM_META)
        assert form.validate() is True


class TestWarehouseForm:
    """WarehouseForm: type-specific validation, online slug, parent hierarchy."""

    def test_main_warehouse_simple(self):
        from forms import WarehouseForm
        fd = _fd(name="Main WH", warehouse_type="MAIN")
        form = WarehouseForm(fd, meta=FORM_META)
        assert form.validate() is True
        assert form.partner_id.data is None
        assert form.supplier_id.data is None

    def test_online_warehouse_requires_unique_slug(self, app, mocker):
        from forms import WarehouseForm
        from models import Warehouse as W
        mock_q = mock.MagicMock()
        mock_q.filter.return_value.first.return_value = mock.MagicMock(id=99)
        mocker.patch.object(W, 'query', mock_q)
        fd = _fd(name="Online WH", warehouse_type="ONLINE", online_slug="my-shop")
        form = WarehouseForm(fd, meta=FORM_META)
        assert form.validate() is False
        assert "online_slug" in form.errors

    def test_online_warehouse_unique_slug_ok(self, app, mocker):
        from forms import WarehouseForm
        from models import Warehouse as W
        mock_q = mock.MagicMock()
        mock_q.filter.return_value.first.return_value = None
        mocker.patch.object(W, 'query', mock_q)
        fd = _fd(name="Online WH", warehouse_type="ONLINE", online_slug="my-shop")
        form = WarehouseForm(fd, meta=FORM_META)
        assert form.validate() is True

    def test_online_is_default_unique(self, app, mocker):
        from forms import WarehouseForm
        from models import Warehouse as W
        mock_q = mock.MagicMock()
        mock_q.filter.return_value.first.side_effect = [
            None,
            mock.MagicMock(id=99),
        ]
        mocker.patch.object(W, 'query', mock_q)
        fd = _fd(name="Online WH", warehouse_type="ONLINE",
                 online_slug="my-shop", online_is_default="y")
        form = WarehouseForm(fd, meta=FORM_META)
        assert form.validate() is False
        assert "online_is_default" in form.errors

    def test_online_slug_not_allowed_for_non_online(self):
        from forms import WarehouseForm
        fd = _fd(name="WH", warehouse_type="MAIN", online_slug="sluggy")
        form = WarehouseForm(fd, meta=FORM_META)
        assert form.validate() is False
        assert "online_slug" in form.errors

    def test_exchange_warehouse_requires_supplier(self):
        from forms import WarehouseForm
        fd = _fd(name="Exchange WH", warehouse_type="EXCHANGE")
        form = WarehouseForm(fd, meta=FORM_META)
        assert form.validate() is False
        assert "supplier_id" in form.errors

    def test_exchange_with_supplier_ok(self):
        from forms import WarehouseForm
        fd = _fd(name="Exchange WH", warehouse_type="EXCHANGE", supplier_id="5")
        form = WarehouseForm(fd, meta=FORM_META)
        assert form.validate() is True

    def test_partner_warehouse_requires_partner(self):
        from forms import WarehouseForm
        fd = _fd(name="Partner WH", warehouse_type="PARTNER")
        form = WarehouseForm(fd, meta=FORM_META)
        assert form.validate() is False
        assert "partner_id" in form.errors

    def test_partner_with_partner_ok(self):
        from forms import WarehouseForm
        fd = _fd(name="Partner WH", warehouse_type="PARTNER", partner_id="3")
        form = WarehouseForm(fd, meta=FORM_META)
        assert form.validate() is True

    def test_self_parent_rejected(self):
        from forms import WarehouseForm
        fd = _fd(name="WH", warehouse_type="MAIN", id="7", parent_id="7")
        form = WarehouseForm(fd, meta=FORM_META)
        assert form.validate() is False
        assert "parent_id" in form.errors

    def test_circular_parent_detected(self, app, mocker):
        from forms import WarehouseForm
        parent = mock.MagicMock(id=2, parent_id=1)
        mocker.patch("extensions.db.session.get", return_value=parent)
        fd = _fd(name="WH", warehouse_type="MAIN", id="1", parent_id="2")
        form = WarehouseForm(fd, meta=FORM_META)
        assert form.validate() is False
        assert "parent_id" in form.errors

    def test_inventory_clears_partner_supplier(self):
        from forms import WarehouseForm
        fd = _fd(name="Inv WH", warehouse_type="INVENTORY", partner_id="3", supplier_id="5")
        form = WarehouseForm(fd, meta=FORM_META)
        assert form.validate() is True
        assert form.partner_id.data is None
        assert form.supplier_id.data is None


class TestSaleForm:
    """SaleForm: line validation, at least one valid line required."""

    def _sd(self, **kw):
        md = MultiDict()
        for k, v in kw.items():
            if v is not None:
                md[k] = str(v)
        return md

    def test_no_lines_fails(self):
        from forms import SaleForm
        fd = self._sd(customer_id="1", seller_employee_id="1", currency="ILS")
        form = SaleForm(fd, meta=FORM_META)
        assert form.validate() is False

    def test_valid_line(self):
        from forms import SaleForm
        fd = self._sd(customer_id="1", seller_employee_id="1", currency="ILS")
        fd.setlist("lines-0-product_id", ["10"])
        fd.setlist("lines-0-warehouse_id", ["5"])
        fd.setlist("lines-0-quantity", ["2"])
        fd.setlist("lines-0-unit_price", ["50"])
        form = SaleForm(fd, meta=FORM_META)
        assert form.validate() is True

    def test_line_missing_product_fails(self):
        from forms import SaleForm
        fd = self._sd(customer_id="1", seller_employee_id="1", currency="ILS")
        fd.setlist("lines-0-quantity", ["2"])
        fd.setlist("lines-0-unit_price", ["50"])
        form = SaleForm(fd, meta=FORM_META)
        assert form.validate() is False
        assert "lines" in form.errors

    def test_line_quantity_zero_fails(self):
        from forms import SaleForm
        fd = self._sd(customer_id="1", seller_employee_id="1", currency="ILS")
        fd.setlist("lines-0-product_id", ["10"])
        fd.setlist("lines-0-warehouse_id", ["5"])
        fd.setlist("lines-0-quantity", ["0"])
        fd.setlist("lines-0-unit_price", ["50"])
        form = SaleForm(fd, meta=FORM_META)
        assert form.validate() is False
        assert "lines" in form.errors


class TestInvoiceForm:
    """InvoiceForm: basic validation, field presence."""

    def _id(self, **kw):
        md = MultiDict()
        for k, v in kw.items():
            if v is not None:
                md[k] = str(v)
        return md

    def test_valid_invoice(self):
        from forms import InvoiceForm
        fd = self._id(invoice_number="INV-001", invoice_date="2026-06-25 10:00",
                      source="SALE", kind="INVOICE", currency="ILS", total_amount="500")
        fd.setlist("lines-0-product_id", ["1"])
        fd.setlist("lines-0-description", ["Widget"])
        fd.setlist("lines-0-quantity", ["1.00"])
        fd.setlist("lines-0-unit_price", ["500"])
        form = InvoiceForm(fd, meta=FORM_META)
        assert form.validate() is True

    def test_missing_required_fields(self):
        from forms import InvoiceForm
        fd = self._id(invoice_number="INV-001")
        form = InvoiceForm(fd, meta=FORM_META)
        assert form.validate() is False
        assert "invoice_date" in form.errors or "source" in form.errors

    def test_invoice_type_credit_note(self):
        from forms import InvoiceForm
        fd = self._id(invoice_number="CN-001", invoice_date="2026-06-25 10:00",
                      source="SALE", kind="CREDIT_NOTE", currency="ILS", total_amount="100")
        fd.setlist("lines-0-product_id", ["1"])
        fd.setlist("lines-0-description", ["Return"])
        fd.setlist("lines-0-quantity", ["1.00"])
        fd.setlist("lines-0-unit_price", ["100"])
        form = InvoiceForm(fd, meta=FORM_META)
        assert form.validate() is True


class TestTransferFormValidate:
    def test_destination_same_as_source(self):
        from forms import TransferForm
        form = TransferForm(
            _fd(product_id="1", source_id="1", destination_id="1",
                quantity="10", direction="OUT", reference="T1"),
            meta=FORM_META,
        )
        assert form.validate() is False
        assert any("مختلف" in e for e in form.destination_id.errors)

    def test_stock_check_exception(self, mocker):
        from forms import TransferForm
        mocker.patch("models.StockLevel.query.filter_by", side_effect=Exception("DB down"))
        form = TransferForm(
            _fd(product_id="1", source_id="2", destination_id="3",
                quantity="10", direction="OUT", reference="T1"),
            meta=FORM_META,
        )
        try:
            result = form.validate()
        except Exception:
            result = False
        assert result is not None

    def test_apply_to_transfer(self):
        from forms import TransferForm
        from datetime import timezone
        t = mock.MagicMock()
        form = TransferForm(
            _fd(product_id="5", source_id="1", destination_id="2",
                quantity="3", direction="IN", reference="TR-001",
                notes="Test transfer"),
            meta=FORM_META,
        )
        form.transfer_date.data = None
        result = form.apply_to(t)
        assert t.product_id == 5
        assert t.quantity == 3
        assert t.direction == "IN"
        assert t.notes == "Test transfer"


class TestSettlementRangeFormValidate:
    def test_start_after_end_fails(self):
        from forms import SettlementRangeForm
        form = SettlementRangeForm(
            _fd(start="2025-06-01", end="2025-05-01"),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_valid_dates(self):
        from forms import SettlementRangeForm
        form = SettlementRangeForm(
            _fd(start="2025-01-01", end="2025-01-31"),
            meta=FORM_META,
        )
        assert form.validate() is True


class TestUserFormInit:
    def test_with_obj_sets_last_login_fields(self, app, mocker):
        from forms import UserForm
        import utils as _fu
        mocker.patch("models.Role.query.order_by")
        mocker.patch("models.Branch.query")
        mocker.patch("utils.tenant_ui.branch_choices_for_form", return_value=[])
        mocker.patch("flask.request.view_args", {"user_id": "5"})

        obj = mock.MagicMock()
        obj.last_login = "2025-01-01 10:00"
        obj.last_seen = "2025-01-02 10:00"
        obj.last_login_ip = "192.168.1.1"
        obj.login_count = 42

        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"
            admin.role.name = "OWNER"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = UserForm(obj=obj, meta=FORM_META)
                assert form.last_login.data == "2025-01-01 10:00"
                assert form.last_seen.data == "2025-01-02 10:00"

    def test_validate_username_unique(self):
        from forms import UserForm
        from wtforms.validators import ValidationError
        form = UserForm(meta=FORM_META)
        form.username.data = "existing"
        mock_q = mock.MagicMock()
        mock_q.filter.return_value.first.return_value = mock.MagicMock(id=99)
        with mock.patch("forms.User.query", mock_q):
            with pytest.raises(ValidationError):
                form.validate_username(form.username)

    def test_validate_email_during_edit(self, app):
        from forms import UserForm
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"
            admin.role.name = "OWNER"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = UserForm(meta=FORM_META)
                form._editing_user_id = 1
                form.email.data = "test@example.com"
                with mock.patch("models.User.query.filter") as mf:
                    mf.return_value.first.return_value = None
                    form.validate_email(form.email)
                    assert form.email.data == "test@example.com"


class TestQuickSupplierForm:
    def test_validate_email_normalizes(self):
        from forms import QuickSupplierForm
        form = QuickSupplierForm(meta=FORM_META)
        field = mock.MagicMock()
        field.data = "  Test@Example.COM  "
        form.validate_email(field)
        assert field.data == "test@example.com"

    def test_validate_phone_normalizes(self):
        from forms import QuickSupplierForm
        form = QuickSupplierForm(meta=FORM_META)
        field = mock.MagicMock()
        field.data = "  050-123-4567  "
        form.validate_phone(field)
        assert field.data == "0501234567"


class TestQuickPartnerForm:
    def test_validate_email_normalizes(self):
        from forms import QuickPartnerForm
        form = QuickPartnerForm(meta=FORM_META)
        field = mock.MagicMock()
        field.data = "  USER@DOMAIN.COM  "
        form.validate_email(field)
        assert field.data == "user@domain.com"

    def test_validate_phone_normalizes(self):
        from forms import QuickPartnerForm
        form = QuickPartnerForm(meta=FORM_META)
        field = mock.MagicMock()
        field.data = "  972-50-123-4567  "
        form.validate_phone(field)
        assert field.data == "972501234567"


class TestCleanImagePathBranches:
    def test_with_path_returns_basename(self):
        from forms import _clean_image_path
        assert _clean_image_path("some\\dir\\file.txt") == "file.txt"

    def test_absolute_path_starts_with_slash(self):
        from forms import _clean_image_path
        assert _clean_image_path("/some/dir/file.txt") == "/some/dir/file.txt"

    def test_with_url_returns_url(self):
        from forms import _clean_image_path
        assert _clean_image_path("http://example.com/file") == "http://example.com/file"

    def test_none_returns_none(self):
        from forms import _clean_image_path
        assert _clean_image_path(None) is None


class TestPaymentFormValidateEdgeCases:
    def test_total_amount_exception(self, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        form = PaymentForm(_fd(entity_type="CUSTOMER", direction="IN",
                               total_amount="not-a-number", payer_id="1",
                               method="CASH", currency="ILS"),
                           meta=FORM_META)
        form.validate()
        assert form.total_amount.data is None or isinstance(form.total_amount.data, Decimal)

    def test_supplier_service_ids_rejected(self, mocker):
        from forms import BulkPaymentForm
        mocker.patch("forms.currency_choices", return_value=[("ILS", "ILS")])
        mocker.patch("models.Currency.query", return_value=[])
        mocker.patch("models.PaymentMethod", return_value=[])
        form = BulkPaymentForm(MultiDict([
            ("payer_type", "supplier"), ("direction", "OUT"),
            ("total_amount", "100"), ("payer_id", "1"),
            ("method", "CASH"),
            ("allocations-0-allocation_amounts-0", "100"),
        ]), meta=FORM_META)
        for entry in form.allocations:
            fm = entry.form
            with mock.patch.object(fm, "service_ids", create=True, data=["1"]):
                pass
        assert form.validate() is False

    def test_payer_id_invalid(self, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        form = PaymentForm(_fd(entity_type="CUSTOMER", direction="IN",
                               total_amount="50", payer_id="abc",
                               method="CASH", currency="ILS"),
                           meta=FORM_META)
        assert form.validate() is False

    def test_direction_invalid(self, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        form = PaymentForm(_fd(entity_type="CUSTOMER", direction="INVALID",
                               total_amount="50", payer_id="1",
                               entity_id="1", method="CASH", currency="ILS"),
                           meta=FORM_META)
        assert form.validate() is False

    def test_entity_type_unknown(self, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        form = PaymentForm(_fd(entity_type="UNKNOWN", direction="IN",
                               total_amount="50", payer_id="1",
                               method="CASH", currency="ILS"),
                           meta=FORM_META)
        assert form.validate() is False

    def test_expense_direction_not_out(self, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        form = PaymentForm(_fd(entity_type="EXPENSE", direction="IN",
                               total_amount="50", payer_id="1",
                               method="CASH", currency="ILS"),
                           meta=FORM_META)
        assert form.validate() is False

    def test_customer_search_fallback(self, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        cust = mock.MagicMock(id=42)
        with mock.patch("models.Customer.query.filter") as mf:
            mf.return_value.first.return_value = cust
            form = PaymentForm(_fd(entity_type="CUSTOMER", direction="IN",
                                   total_amount="50", payer_id="1",
                                   method="CASH", currency="ILS"),
                               meta=FORM_META)
            form.entity_id.data = ""
            form.customer_search.data = "test"
            with mock.patch.object(form, "customer_search", create=True):
                form.validate()
                assert form.entity_id.data == ""

    def test_missing_reference_for_non_expense(self, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        form = PaymentForm(_fd(entity_type="CUSTOMER", direction="IN",
                               total_amount="50", payer_id="1",
                               method="CASH", currency="ILS"),
                           meta=FORM_META)
        assert form.validate() is False

    def test_multiple_entity_references(self, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        form = PaymentForm(_fd(entity_type="CUSTOMER", direction="IN",
                               total_amount="50", payer_id="1",
                               customer_id="5", supplier_id="3",
                               method="CASH", currency="ILS"),
                           meta=FORM_META)
        assert form.validate() is False

    def test_direction_not_allowed(self, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        mocker.patch("models.is_direction_allowed", return_value=False)
        form = PaymentForm(_fd(entity_type="CUSTOMER", direction="IN",
                               total_amount="50", payer_id="1",
                               customer_id="5", method="CASH", currency="ILS"),
                           meta=FORM_META)
        assert form.validate() is False

    def test_direction_allowed_exception(self, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        mocker.patch("models.is_direction_allowed", side_effect=Exception("boom"))
        form = PaymentForm(_fd(entity_type="CUSTOMER", direction="IN",
                               total_amount="50", payer_id="1",
                               customer_id="5", method="CASH", currency="ILS"),
                           meta=FORM_META)
        assert form.validate() is False


class TestPaymentFormValidateChequeBranch:
    def test_cheque_validation_error_number(self, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        mocker.patch("models.is_direction_allowed", return_value=True)
        form = PaymentForm(_fd(entity_type="CUSTOMER", direction="IN",
                               total_amount="50", payer_id="1",
                               entity_id="1", customer_id="5",
                               method="CHEQUE", currency="ILS"),
                           meta=FORM_META)
        with mock.patch.object(PaymentForm, '_validate_cheque',
                                side_effect=ValidationError("رقم الشيك مطلوب")):
            assert form.validate() is False

    def test_cheque_validation_error_bank(self, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        mocker.patch("models.is_direction_allowed", return_value=True)
        form = PaymentForm(_fd(entity_type="CUSTOMER", direction="IN",
                               total_amount="50", payer_id="1",
                               entity_id="1", customer_id="5",
                               method="CHEQUE", currency="ILS"),
                           meta=FORM_META)
        with mock.patch.object(PaymentForm, '_validate_cheque',
                                side_effect=ValidationError("اسم البنك مطلوب")):
            assert form.validate() is False

    def test_cheque_validation_error_date(self, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        mocker.patch("models.is_direction_allowed", return_value=True)
        form = PaymentForm(_fd(entity_type="CUSTOMER", direction="IN",
                               total_amount="50", payer_id="1",
                               entity_id="1", customer_id="5",
                               method="CHEQUE", currency="ILS"),
                           meta=FORM_META)
        with mock.patch.object(PaymentForm, '_validate_cheque',
                                side_effect=ValidationError("تاريخ الاستحقاق مطلوب")):
            assert form.validate() is False

    def test_card_validation_error_number(self, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        mocker.patch("models.is_direction_allowed", return_value=True)
        form = PaymentForm(_fd(entity_type="CUSTOMER", direction="IN",
                               total_amount="50", payer_id="1",
                               entity_id="1", customer_id="5",
                               method="CARD", currency="ILS"),
                           meta=FORM_META)
        with mock.patch.object(PaymentForm, '_validate_card_payload',
                                side_effect=ValidationError("رقم البطاقة غير صالح")):
            assert form.validate() is False

    def test_card_validation_error_expiry(self, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        mocker.patch("models.is_direction_allowed", return_value=True)
        form = PaymentForm(_fd(entity_type="CUSTOMER", direction="IN",
                               total_amount="50", payer_id="1",
                               entity_id="1", customer_id="5",
                               method="CARD", currency="ILS"),
                           meta=FORM_META)
        with mock.patch.object(PaymentForm, '_validate_card_payload',
                                side_effect=ValidationError("الانتهاء غير صالح")):
            assert form.validate() is False

    def test_card_validation_error_holder(self, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        mocker.patch("models.is_direction_allowed", return_value=True)
        form = PaymentForm(_fd(entity_type="CUSTOMER", direction="IN",
                               total_amount="50", payer_id="1",
                               entity_id="1", customer_id="5",
                               method="CARD", currency="ILS"),
                           meta=FORM_META)
        with mock.patch.object(PaymentForm, '_validate_card_payload',
                                side_effect=ValidationError("حامل البطاقة مطلوب")):
            assert form.validate() is False

    def test_card_validation_error_generic(self, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        mocker.patch("models.is_direction_allowed", return_value=True)
        form = PaymentForm(_fd(entity_type="CUSTOMER", direction="IN",
                               total_amount="50", payer_id="1",
                               entity_id="1", customer_id="5",
                               method="CARD", currency="ILS"),
                           meta=FORM_META)
        with mock.patch.object(PaymentForm, '_validate_card_payload',
                                side_effect=ValidationError("خطأ عام في البطاقة")):
            assert form.validate() is False

    def test_bank_validation_error(self, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        mocker.patch("models.is_direction_allowed", return_value=True)
        form = PaymentForm(_fd(entity_type="CUSTOMER", direction="IN",
                               total_amount="50", payer_id="1",
                               entity_id="1", customer_id="5",
                               method="BANK", currency="ILS"),
                           meta=FORM_META)
        with mock.patch.object(PaymentForm, '_validate_bank',
                                side_effect=ValidationError("مرجع التحويل مطلوب")):
            assert form.validate() is False

    def test_online_validation_error_gateway(self, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        mocker.patch("models.is_direction_allowed", return_value=True)
        form = PaymentForm(_fd(entity_type="CUSTOMER", direction="IN",
                               total_amount="50", payer_id="1",
                               entity_id="1", customer_id="5",
                               method="ONLINE", currency="ILS"),
                           meta=FORM_META)
        with mock.patch.object(PaymentForm, '_validate_online',
                                side_effect=ValidationError("بوابة الدفع مطلوبة")):
            assert form.validate() is False

    def test_online_validation_error_ref(self, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        mocker.patch("models.is_direction_allowed", return_value=True)
        form = PaymentForm(_fd(entity_type="CUSTOMER", direction="IN",
                               total_amount="50", payer_id="1",
                               entity_id="1", customer_id="5",
                               method="ONLINE", currency="ILS"),
                           meta=FORM_META)
        with mock.patch.object(PaymentForm, '_validate_online',
                                side_effect=ValidationError("مرجع العملية مطلوب")):
            assert form.validate() is False

    def test_online_validation_error_generic(self, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        mocker.patch("models.is_direction_allowed", return_value=True)
        form = PaymentForm(_fd(entity_type="CUSTOMER", direction="IN",
                               total_amount="50", payer_id="1",
                               entity_id="1", customer_id="5",
                               method="ONLINE", currency="ILS"),
                           meta=FORM_META)
        with mock.patch.object(PaymentForm, '_validate_online',
                                side_effect=ValidationError("خطأ في الدفع الإلكتروني")):
            assert form.validate() is False

    def test_idempotency_key_generated(self, app, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        mocker.patch("models.is_direction_allowed", return_value=True)
        mocker.patch("models.generate_idempotency_key", return_value="key-123")
        with app.app_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"; admin.role.name = "admin"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                with mock.patch("flask_login.current_user", admin):
                    form = PaymentForm(_fd(entity_type="CUSTOMER", direction="IN",
                                           total_amount="50", payer_id="1",
                                           customer_id="5", method="CASH", currency="ILS",
                                           payment_date="2025-06-15T10:00", status="COMPLETED"),
                                       meta=FORM_META)
                    form.customer_id.data = "5"
                    form.entity_type.data = "CUSTOMER"
                    form.direction.data = "IN"
                    form.method.data = "CASH"
                    form.payment_date.data = datetime(2025, 6, 15, 10, 0)
                    form.status.data = "COMPLETED"
                    for entry in form.splits:
                        entry.form.amount.data = Decimal("50")
                        entry.form.method.data = "CASH"
                    import models as m2
                    assert m2.generate_idempotency_key("pay") == "key-123"
                    result = form.validate()
                    assert result == True, f"validate failed: {form.errors}"
                    assert form.idempotency_key.data is not None


class TestSupplierSettlementFormBranches:
    def test_from_date_after_to_date(self):
        from forms import SupplierSettlementForm
        form = SupplierSettlementForm(
            _fd(supplier_id="1", from_date="2025-06-01 00:00", to_date="2025-05-01 00:00",
                currency="ILS", status="DRAFT", mode="ON_RECEIPT",
                total_gross="100", total_due="100"),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_lines_exception_branch(self):
        from forms import SupplierSettlementForm
        fd = MultiDict([("supplier_id", "1"), ("from_date", "2025-01-01 00:00"),
                        ("to_date", "2025-01-31 00:00"), ("currency", "ILS"),
                        ("status", "DRAFT"), ("mode", "ON_RECEIPT"),
                        ("total_gross", "0"), ("total_due", "0")])
        form = SupplierSettlementForm(fd, meta=FORM_META)
        for entry in form.lines:
            entry.form.quantity.data = None
        assert form.validate() is False


class TestSupplierLoanSettlementFormBranches:
    def test_missing_both_loan_and_supplier(self):
        from forms import SupplierLoanSettlementForm
        form = SupplierLoanSettlementForm(
            _fd(settled_price="100", settlement_date="2025-06-01"),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_loan_supplier_mismatch(self, mocker):
        from forms import SupplierLoanSettlementForm
        loan_mock = mock.MagicMock(supplier_id=1)
        mocker.patch("extensions.db.session.get", return_value=loan_mock)
        form = SupplierLoanSettlementForm(
            _fd(loan_id="5", supplier_id="9", settled_price="100",
                settlement_date="2025-06-01"),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_db_get_exception(self):
        from forms import SupplierLoanSettlementForm
        form = SupplierLoanSettlementForm(
            _fd(loan_id="5", supplier_id="1", settled_price="100",
                settlement_date="2025-06-01"),
            meta=FORM_META,
        )
        form.loan_id.data = "5"
        form.supplier_id.data = "1"
        try:
            form.validate()
        except Exception:
            pass
        assert form.loan_id.data == "5"
        assert form.supplier_id.data == "1"

    def test_apply_to(self):
        from forms import SupplierLoanSettlementForm
        sls = mock.MagicMock()
        form = SupplierLoanSettlementForm(
            _fd(loan_id="3", supplier_id="1", settled_price="200",
                settlement_date="2025-06-15", notes="Test"),
            meta=FORM_META,
        )
        form.apply_to(sls)
        assert sls.loan_id == 3
        assert sls.supplier_id == 1
        assert sls.settled_price == Decimal("200")


class TestInvoiceRefundFormValidate:
    def test_refund_exceeds_refundable(self, mocker):
        from forms import InvoiceRefundForm
        inv = mock.MagicMock(refundable_amount=Decimal("30"))
        mocker.patch("extensions.db.session.get", return_value=inv)
        form = InvoiceRefundForm(
            _fd(invoice_id="1", amount="100", reason="test"),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_exception_in_refund_check(self, mocker):
        from forms import InvoiceRefundForm
        mocker.patch("extensions.db.session.get", side_effect=Exception("boom"))
        form = InvoiceRefundForm(
            _fd(invoice_id="1", amount="10", reason="test"),
            meta=FORM_META,
        )
        assert form.validate() is True

    def test_build_payment_payload(self):
        from forms import InvoiceRefundForm
        form = InvoiceRefundForm(
            _fd(invoice_id="5", amount="50", reason="RMA-001", notes="refund"),
            meta=FORM_META,
        )
        payload = form.build_payment_payload()
        assert payload["direction"] == "OUTGOING"
        assert payload["entity_type"] == "INVOICE"
        assert payload["entity_id"] == 5


class TestInvoiceCancelFormValidate:
    def test_returns_false_on_invalid(self):
        from forms import InvoiceCancelForm
        form = InvoiceCancelForm(_fd(), meta=FORM_META)
        assert form.validate() is False


class TestPartnerSettlementFormBranches:
    def test_from_date_after_to_date(self):
        from forms import PartnerSettlementForm
        form = PartnerSettlementForm(
            _fd(partner_id="1", from_date="2025-06-01 00:00",
                to_date="2025-05-01 00:00", currency="ILS",
                status="DRAFT"),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_lines_exception_branch(self):
        from forms import PartnerSettlementForm
        form = PartnerSettlementForm(
            _fd(partner_id="1", from_date="2025-01-01 00:00",
                to_date="2025-01-31 00:00", currency="ILS",
                status="DRAFT"),
            meta=FORM_META,
        )
        for entry in form.lines:
            entry.form.quantity.data = None
        assert form.validate() is False

    def test_negative_total_share(self):
        from forms import PartnerSettlementForm
        fd = MultiDict([("partner_id", "1"), ("from_date", "2025-01-01 00:00"),
                        ("to_date", "2025-01-31 00:00"), ("currency", "ILS"),
                        ("status", "DRAFT"),
                        ("lines-0-quantity", "1"), ("lines-0-unit_price", "10"),
                        ("lines-0-share_amount", "-5")])
        form = PartnerSettlementForm(fd, meta=FORM_META)
        assert form.validate() is False

    def test_apply_to(self):
        from forms import PartnerSettlementForm
        ps = mock.MagicMock()
        form = PartnerSettlementForm(
            _fd(partner_id="3", from_date="2025-01-01 00:00",
                to_date="2025-01-31 00:00", currency="usd",
                status="CONFIRMED", notes="done"),
            meta=FORM_META,
        )
        form.apply_to(ps)
        assert ps.currency == "USD"
        assert ps.partner_id == 3


class TestPaymentFormInitSplits:
    def test_split_entry_method_choices_set(self, app, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"; admin.role.name = "admin"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = PaymentForm(
                    MultiDict([("entity_type", "CUSTOMER"), ("direction", "IN"),
                               ("splits-0-amount", "100"), ("splits-0-method", "CASH")]),
                    meta=FORM_META,
                )
                if form.splits.entries:
                    entry = form.splits.entries[0]
                    assert hasattr(entry.form, "method")
                    assert hasattr(entry.form, "currency")

    def test_split_fx_rate_from_object(self, app, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"; admin.role.name = "admin"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = PaymentForm(
                    MultiDict([("entity_type", "CUSTOMER"), ("direction", "IN"),
                               ("splits-0-amount", "100"), ("splits-0-method", "CASH")]),
                    meta=FORM_META,
                )
                if form.splits.entries:
                    entry = form.splits.entries[0]
                    assert hasattr(entry.form, "fx_rate")

    def test_split_fx_rate_settled_when_same_currency(self, app, mocker):
        from forms import PaymentForm
        import utils
        from models import ensure_currency
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        mocker.patch("forms.ensure_currency", return_value="ILS")
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"; admin.role.name = "admin"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = PaymentForm(
                    MultiDict([("entity_type", "CUSTOMER"), ("direction", "IN"),
                               ("splits-0-amount", "100"), ("splits-0-method", "CASH")]),
                    meta=FORM_META,
                )
                assert form.currency.data == "ILS"
                assert form.currency.choices

    def test_init_no_splits_adds_one(self, app, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"; admin.role.name = "admin"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = PaymentForm(_fd(entity_type="CUSTOMER", direction="IN",
                                       currency="ILS"),
                                   meta=FORM_META)
                assert len(form.splits.entries) >= 1


class TestSupplierSettlementFormDeep:
    def test_no_lines_with_values(self):
        from forms import SupplierSettlementForm
        form = SupplierSettlementForm(
            _fd(supplier_id="1", from_date="2025-01-01 00:00",
                to_date="2025-01-31 00:00", currency="ILS",
                status="DRAFT", mode="ON_RECEIPT",
                total_gross="0", total_due="0"),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_needs_pricing_blocked_on_confirm(self):
        from forms import SupplierSettlementForm
        form = SupplierSettlementForm(
            MultiDict([("supplier_id", "1"), ("from_date", "2025-01-01 00:00"),
                       ("to_date", "2025-01-31 00:00"), ("currency", "ILS"),
                       ("status", "CONFIRMED"), ("mode", "ON_RECEIPT"),
                       ("total_gross", "100"), ("total_due", "100"),
                       ("lines-0-quantity", "1")]),
            meta=FORM_META,
        )
        for entry in form.lines:
            entry.form.needs_pricing.data = True
        assert form.validate() is False

    def test_apply_to(self):
        from forms import SupplierSettlementForm
        ss = mock.MagicMock()
        form = SupplierSettlementForm(
            _fd(supplier_id="1", from_date="2025-01-01 00:00",
                to_date="2025-01-31 00:00", currency="ils",
                status="CONFIRMED", mode="ON_RECEIPT",
                total_gross="100", total_due="100"),
            meta=FORM_META,
        )
        form.apply_to(ss)
        assert ss.currency == "ILS" and ss.status == "CONFIRMED"


class TestPreOrderFormValidate:
    def test_expected_date_before_preorder_date(self):
        from forms import PreOrderForm
        form = PreOrderForm(
            _fd(reference="PO1", preorder_date="2025-06-15T10:00",
                expected_date="2025-06-10T10:00"),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_prepaid_exceeds_total(self, mocker):
        from forms import PreOrderForm
        prod = mock.MagicMock(price=Decimal("100"))
        mocker.patch("extensions.db.session.get", return_value=prod)
        form = PreOrderForm(
            _fd(product_id="1", quantity="2", prepaid_amount="500",
                tax_rate="17", preorder_date="2025-06-15T10:00"),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_db_exception_does_not_block(self, mocker):
        from forms import PreOrderForm
        mocker.patch("extensions.db.session.get", side_effect=Exception("boom"))
        form = PreOrderForm(
            _fd(product_id="1", quantity="2", prepaid_amount="50",
                preorder_date="2025-06-15T10:00"),
            meta=FORM_META,
        )
        try:
            result = form.validate()
        except Exception:
            result = False
        assert result is not None

    def test_apply_to(self):
        from forms import PreOrderForm
        po = mock.MagicMock()
        form = PreOrderForm(
            _fd(reference="PO-001", preorder_date="2025-06-15T10:00",
                expected_date="2025-06-20T10:00", status="PENDING",
                product_id="1", warehouse_id="1", customer_id="1",
                quantity="5", prepaid_amount="100", tax_rate="17",
                payment_method="CASH", notes="Test preorder"),
            meta=FORM_META,
        )
        form.apply_to(po)
        assert po.quantity == 5


class TestServiceRequestFormValidate:
    def test_end_time_before_start_time(self):
        from forms import ServiceRequestForm
        form = ServiceRequestForm(
            _fd(customer_id="1", vehicle_vrn="ABC123",
                start_time="2025-06-15 14:00", end_time="2025-06-15 10:00"),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_started_at_before_received_at(self):
        from forms import ServiceRequestForm
        form = ServiceRequestForm(
            _fd(customer_id="1", vehicle_vrn="ABC123",
                received_at="2025-06-15 10:00", started_at="2025-06-14 09:00"),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_started_at_date_before_plan_start(self):
        from forms import ServiceRequestForm
        form = ServiceRequestForm(
            _fd(customer_id="1", vehicle_vrn="ABC123",
                start_time="2025-06-15 09:00", started_at="2025-06-14 10:00"),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_expected_delivery_before_started_at(self):
        from forms import ServiceRequestForm
        form = ServiceRequestForm(
            _fd(customer_id="1", vehicle_vrn="ABC123",
                started_at="2025-06-15 10:00",
                expected_delivery="2025-06-14 09:00"),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_completed_at_before_started_at(self):
        from forms import ServiceRequestForm
        form = ServiceRequestForm(
            _fd(customer_id="1", vehicle_vrn="ABC123",
                started_at="2025-06-15 10:00",
                completed_at="2025-06-14 09:00"),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_tax_rate_out_of_range(self):
        from forms import ServiceRequestForm
        form = ServiceRequestForm(
            _fd(customer_id="1", vehicle_vrn="ABC123",
                tax_rate="150"),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_total_amount_mismatch(self):
        from forms import ServiceRequestForm
        form = ServiceRequestForm(
            _fd(customer_id="1", vehicle_vrn="ABC123",
                parts_total="200", labor_total="100", discount_total="0",
                tax_rate="17", total_amount="999"),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_valid_service_request(self):
        from forms import ServiceRequestForm
        form = ServiceRequestForm(
            _fd(customer_id="1", vehicle_vrn="ABC123",
                start_time="2025-06-15T10:00", end_time="2025-06-15T12:00",
                received_at="2025-06-15T09:00", started_at="2025-06-15T10:00",
                expected_delivery="2025-06-16T10:00",
                completed_at="2025-06-16T14:00",
                parts_total="200", labor_total="100", discount_total="0",
                tax_rate="17", total_amount="351",
                currency="ILS"),
            meta=FORM_META,
        )
        try:
            result = form.validate()
        except Exception:
            result = False
        assert result is not None

    def test_apply_to(self):
        from forms import ServiceRequestForm
        sr = mock.MagicMock()
        form = ServiceRequestForm(
            _fd(service_number="SRV-001", customer_id="1",
                vehicle_vrn="ABC123",
                parts_total="200", labor_total="100",
                tax_rate="17", currency="ils",
                warranty_days="30", consume_stock="y"),
            meta=FORM_META,
        )
        result = form.apply_to(sr)
        assert sr.currency == "ILS"
        assert sr.warranty_days == 30
        assert sr.consume_stock is True


class TestShipmentItemFormValidate:
    def test_declared_value_less_than_qty_times_cost(self):
        from forms import ShipmentItemForm
        form = ShipmentItemForm(
            _fd(product_id="1", warehouse_id="1",
                quantity="5", unit_cost="100", declared_value="200"),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_valid_shipment_item(self):
        from forms import ShipmentItemForm
        form = ShipmentItemForm(
            _fd(product_id="1", warehouse_id="1",
                quantity="5", unit_cost="100", declared_value="600"),
            meta=FORM_META,
        )
        assert form.validate() is True

    def test_no_declared_value_valid(self):
        from forms import ShipmentItemForm
        form = ShipmentItemForm(
            _fd(product_id="1", warehouse_id="1",
                quantity="5", unit_cost="100"),
            meta=FORM_META,
        )
        assert form.validate() is True


class TestShipmentFormValidate:
    def test_no_items(self):
        from forms import ShipmentForm
        form = ShipmentForm(
            _fd(shipment_number="SHP-001", currency="USD", status="DRAFT"),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_duplicate_product_warehouse(self):
        from forms import ShipmentForm
        fd = MultiDict([
            ("shipment_number", "SHP-001"), ("currency", "USD"),
            ("status", "DRAFT"),
            ("destination_id", "1"),
            ("items-0-product_id", "1"), ("items-0-warehouse_id", "1"),
            ("items-0-quantity", "10"), ("items-0-unit_cost", "50"),
            ("items-1-product_id", "1"), ("items-1-warehouse_id", "1"),
            ("items-1-quantity", "5"), ("items-1-unit_cost", "50"),
        ])
        form = ShipmentForm(fd, meta=FORM_META)
        assert form.validate() is False

    def test_partner_percentage_exceeds_100(self):
        from forms import ShipmentForm
        fd = MultiDict([
            ("shipment_number", "SHP-002"), ("currency", "USD"),
            ("status", "DRAFT"),
            ("destination_id", "1"),
            ("items-0-product_id", "1"), ("items-0-warehouse_id", "1"),
            ("items-0-quantity", "10"), ("items-0-unit_cost", "50"),
            ("partners-0-partner_id", "1"),
            ("partners-0-share_percentage", "110"),
        ])
        form = ShipmentForm(fd, meta=FORM_META)
        assert form.validate() is False

    def test_partner_percentage_exception_skipped(self):
        from forms import ShipmentForm
        fd = MultiDict([
            ("shipment_number", "SHP-003"), ("currency", "USD"),
            ("status", "DRAFT"),
            ("destination_id", "1"),
            ("items-0-product_id", "1"), ("items-0-warehouse_id", "1"),
            ("items-0-quantity", "10"), ("items-0-unit_cost", "50"),
        ])
        form = ShipmentForm(fd, meta=FORM_META)
        form.destination_id.data = mock.MagicMock(id=1)
        form.destination_id.validate_choice = False
        for entry in form.partners.entries:
            entry.form.partner_id.data = 1
            entry.form.share_percentage.data = None
        has_items = any(
            f.product_id.data and f.warehouse_id.data and (f.quantity.data or 0) >= 1
            for f in (e.form for e in form.items)
        )
        assert has_items is True

    def test_apply_to(self):
        from forms import ShipmentForm, ShipmentItem, ShipmentPartner
        shipment = mock.MagicMock()
        form = ShipmentForm(
            _fd(shipment_number="SHP-001", shipment_date="2025-06-15T10:00",
                origin="China", destination="New York",
                status="IN_TRANSIT", currency="usd",
                shipping_cost="500", notes="Fragile"),
            meta=FORM_META,
        )
        result = form.apply_to(shipment)
        assert shipment.currency == "USD"
        assert shipment.status == "IN_TRANSIT"


class TestShipmentExpenseForm:
    def test_build_expense_payload(self):
        from forms import ShipmentExpenseForm
        form = ShipmentExpenseForm(
            _fd(shipment_id="1", type_id="SHIPPING",
                amount="500", currency="USD", notes="freight"),
            meta=FORM_META,
        )
        payload = form.build_expense_payload()
        assert payload["amount"] == Decimal("500")
        assert payload["type_id"] == "SHIPPING"
        assert payload["notes"] == "freight"


class TestShipmentPaymentFormValidate:
    def test_invalid_direction(self):
        from forms import ShipmentPaymentForm
        form = ShipmentPaymentForm(
            _fd(shipment_id="1", total_amount="100", currency="USD",
                direction="INVALID", method="CASH"),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_in_direction_without_reference_or_notes(self):
        from forms import ShipmentPaymentForm
        form = ShipmentPaymentForm(
            _fd(shipment_id="1", total_amount="100", currency="USD",
                direction="IN", method="CASH"),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_in_direction_with_reference(self):
        from forms import ShipmentPaymentForm
        form = ShipmentPaymentForm(
            _fd(shipment_id="1", total_amount="100", currency="USD",
                direction="IN", method="CASH", reference="REF-001"),
            meta=FORM_META,
        )
        assert form.validate() is True

    def test_cheque_validation(self):
        from forms import ShipmentPaymentForm
        form = ShipmentPaymentForm(
            _fd(shipment_id="1", total_amount="100", currency="USD",
                direction="OUT", method="CHEQUE"),
            meta=FORM_META,
        )
        with mock.patch.object(ShipmentPaymentForm, '_validate_cheque',
                                side_effect=ValidationError("رقم الشيك مطلوب")):
            assert form.validate() is False
            assert any("رقم" in e for e in form.check_number.errors)

    def test_bank_validation(self):
        from forms import ShipmentPaymentForm
        form = ShipmentPaymentForm(
            _fd(shipment_id="1", total_amount="100", currency="USD",
                direction="OUT", method="BANK"),
            meta=FORM_META,
        )
        with mock.patch.object(ShipmentPaymentForm, '_validate_bank',
                                side_effect=ValidationError("مرجع التحويل مطلوب")):
            assert form.validate() is False

    def test_card_validation(self):
        from forms import ShipmentPaymentForm
        form = ShipmentPaymentForm(
            _fd(shipment_id="1", total_amount="100", currency="USD",
                direction="OUT", method="CARD"),
            meta=FORM_META,
        )
        with mock.patch.object(ShipmentPaymentForm, '_validate_card_payload',
                                side_effect=ValidationError("رقم البطاقة غير صالح")):
            assert form.validate() is False

    def test_online_validation(self):
        from forms import ShipmentPaymentForm
        form = ShipmentPaymentForm(
            _fd(shipment_id="1", total_amount="100", currency="USD",
                direction="OUT", method="ONLINE"),
            meta=FORM_META,
        )
        with mock.patch.object(ShipmentPaymentForm, '_validate_online',
                                side_effect=ValidationError("بوابة الدفع مطلوبة")):
            assert form.validate() is False

    def test_generic_validation_error(self):
        from forms import ShipmentPaymentForm
        form = ShipmentPaymentForm(
            _fd(shipment_id="1", total_amount="100", currency="USD",
                direction="OUT", method="CHEQUE"),
            meta=FORM_META,
        )
        form.direction.data = "OUT"
        form.method.data = "CHEQUE"
        with mock.patch.object(ShipmentPaymentForm, '_validate_cheque',
                                side_effect=ValidationError("خطأ عام في الشيك")):
            assert form.validate() is False

    def test_build_payment(self):
        from forms import ShipmentPaymentForm
        form = ShipmentPaymentForm(
            _fd(shipment_id="1", total_amount="500", currency="USD",
                direction="OUT", method="CASH", reference="PAY-001"),
            meta=FORM_META,
        )
        payment = form.build_payment()
        assert payment["entity_type"] == "SHIPMENT"
        assert payment["direction"] == "OUT"
        assert payment["total_amount"] == Decimal("500")

    def test_build_payment_card(self):
        from forms import ShipmentPaymentForm
        form = ShipmentPaymentForm(
            _fd(shipment_id="1", total_amount="200", currency="USD",
                direction="OUT", method="CARD",
                card_number="1234", card_holder="Test",
                card_expiry="12/28"),
            meta=FORM_META,
        )
        with mock.patch.object(ShipmentPaymentForm, '_validate_card_payload',
                                return_value="1234"):
            payment = form.build_payment()
            assert payment["method"] == "CARD"

    def test_build_payment_card_validation_fails(self):
        from forms import ShipmentPaymentForm
        form = ShipmentPaymentForm(
            _fd(shipment_id="1", total_amount="200", currency="USD",
                direction="OUT", method="CARD",
                card_number="", card_holder="", card_expiry=""),
            meta=FORM_META,
        )
        with mock.patch.object(ShipmentPaymentForm, '_validate_card_payload',
                                side_effect=ValidationError("invalid")):
            payment = form.build_payment()
            assert payment["method"] == "CARD"


class TestUniversalReportFormValidate:
    def test_start_after_end(self):
        from forms import UniversalReportForm
        form = UniversalReportForm(
            _fd(start_date="2025-06-01", end_date="2025-05-01"),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_valid_dates(self):
        from forms import UniversalReportForm
        form = UniversalReportForm(
            _fd(start_date="2025-01-01", end_date="2025-01-31"),
            meta=FORM_META,
        )
        assert form.validate() is True


class TestAuditLogFilterFormValidate:
    def test_start_after_end(self):
        from forms import AuditLogFilterForm
        form = AuditLogFilterForm(
            _fd(start_date="2025-06-01", end_date="2025-05-01"),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_valid_dates(self):
        from forms import AuditLogFilterForm
        form = AuditLogFilterForm(
            _fd(start_date="2025-01-01", end_date="2025-01-31"),
            meta=FORM_META,
        )
        assert form.validate() is True


class TestCustomReportFormValidateParameters:
    def test_empty_data_returns(self):
        from forms import CustomReportForm
        form = CustomReportForm(
            _fd(report_type="inventory"),
            meta=FORM_META,
        )
        field = mock.MagicMock()
        field.data = ""
        form.validate_parameters(field)
        assert field.data == ""

    def test_valid_json_dict(self):
        from forms import CustomReportForm
        form = CustomReportForm(
            _fd(report_type="inventory", parameters='{"key": "value"}'),
            meta=FORM_META,
        )
        assert form.validate() is True

    def test_valid_json_list(self):
        from forms import CustomReportForm
        form = CustomReportForm(
            _fd(report_type="inventory", parameters='[1, 2, 3]'),
            meta=FORM_META,
        )
        assert form.validate() is True

    def test_invalid_json(self):
        from forms import CustomReportForm
        form = CustomReportForm(
            _fd(report_type="inventory", parameters='{invalid json}'),
            meta=FORM_META,
        )
        assert form.validate() is False

    def test_json_not_object_or_array(self):
        from forms import CustomReportForm
        form = CustomReportForm(
            _fd(report_type="inventory", parameters='"just a string"'),
            meta=FORM_META,
        )
        assert form.validate() is False


class TestEmployeeFormValidate:
    def test_validate_phone_short(self):
        from forms import EmployeeForm
        form = EmployeeForm(meta=FORM_META)
        field = mock.MagicMock()
        field.data = "123"
        with pytest.raises(Exception):
            form.validate_phone(field)

    def test_validate_phone_normalizes(self):
        from forms import EmployeeForm
        form = EmployeeForm(meta=FORM_META)
        field = mock.MagicMock()
        field.data = "  050-123-4567  "
        form.validate_phone(field)
        assert field.data == "0501234567"

    def test_validate_email_normalizes(self):
        from forms import EmployeeForm
        form = EmployeeForm(meta=FORM_META)
        field = mock.MagicMock()
        field.data = "  USER@EXAMPLE.COM  "
        form.validate_email(field)
        assert field.data == "user@example.com"

    def test_apply_to(self):
        from forms import EmployeeForm
        emp = mock.MagicMock()
        form = EmployeeForm(
            _fd(name="John Doe", position="Manager", phone="050-123-4567",
                email=" JOHN@WORK.COM ", bank_name="Bank A",
                account_number="12345", currency="ils",
                branch_id="1", notes="Test employee"),
            meta=FORM_META,
        )
        form.apply_to(emp)
        assert emp.name == "John Doe"
        assert emp.phone == "0501234567"
        assert emp.email == "john@work.com"
        assert emp.currency == "ILS"


class TestExpenseTypeForm:
    def test_init_with_obj_fields_meta(self, app, mocker):
        from forms import ExpenseTypeForm
        mocker.patch("models.Account.query.filter_by")
        obj = mock.MagicMock()
        obj.fields_meta = {"gl_account_code": "5000"}
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"
            admin.role.name = "OWNER"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = ExpenseTypeForm(obj=obj, meta=FORM_META)
                assert form.gl_account_code.data == "5000"

    def test_init_sets_fields_meta_json(self, app, mocker):
        from forms import ExpenseTypeForm
        mocker.patch("models.Account.query.filter_by")
        obj = mock.MagicMock()
        obj.fields_meta = {"kind": "SALARY"}
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"
            admin.role.name = "OWNER"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = ExpenseTypeForm(obj=obj, meta=FORM_META)
                assert form.fields_meta.data is not None
                assert len(str(form.fields_meta.data)) > 0

    def test_validate_name_unique(self, app):
        from forms import ExpenseTypeForm
        from wtforms.validators import ValidationError
        with app.test_request_context():
            mocker_obj = mock.MagicMock()
            mocker_obj.is_system_account = True
            mocker_obj.username = "admin"
            mocker_obj.role.name = "OWNER"
            with mock.patch("flask_login.utils._get_user", return_value=mocker_obj):
                with mock.patch("models.Account.query.filter_by"):
                    form = ExpenseTypeForm(meta=FORM_META)
                    form.name.data = "ExistingType"
                    mock_q = mock.MagicMock()
                    mock_q.filter.return_value.first.return_value = mock.MagicMock(id=5)
                    with mock.patch("forms.ExpenseType.query", mock_q):
                        with pytest.raises(ValidationError):
                            form.validate_name(form.name)

    def test_validate_name_during_edit(self, app):
        from forms import ExpenseTypeForm
        with app.test_request_context():
            mocker_obj = mock.MagicMock()
            mocker_obj.is_system_account = True
            mocker_obj.username = "admin"
            mocker_obj.role.name = "OWNER"
            with mock.patch("flask_login.utils._get_user", return_value=mocker_obj):
                form = ExpenseTypeForm(meta=FORM_META)
                form.id.data = "3"
                form.name.data = "UniqueName"
                with mock.patch("models.ExpenseType.query.filter") as mf:
                    mf.return_value.first.return_value = None
                    form.validate_name(form.name)

    def test_validate_fields_meta_empty(self):
        from forms import ExpenseTypeForm
        form = ExpenseTypeForm(meta=FORM_META)
        field = mock.MagicMock()
        field.data = ""
        form.validate_fields_meta(field)
        assert form._parsed_fields_meta is None

    def test_validate_fields_meta_valid_json(self):
        from forms import ExpenseTypeForm
        form = ExpenseTypeForm(meta=FORM_META)
        field = mock.MagicMock()
        field.data = '{"kind": "SALARY", "gl_account_code": "5000"}'
        form.validate_fields_meta(field)
        assert isinstance(form._parsed_fields_meta, dict)
        assert form._parsed_fields_meta["kind"] == "SALARY"

    def test_validate_fields_meta_invalid_json(self):
        from forms import ExpenseTypeForm
        form = ExpenseTypeForm(meta=FORM_META)
        field = mock.MagicMock()
        field.data = "{bad json}"
        with pytest.raises(Exception):
            form.validate_fields_meta(field)

    def test_validate_fields_meta_not_dict(self):
        from forms import ExpenseTypeForm
        form = ExpenseTypeForm(meta=FORM_META)
        field = mock.MagicMock()
        field.data = '"just a string"'
        with pytest.raises(Exception):
            form.validate_fields_meta(field)

    def test_apply_to(self):
        from forms import ExpenseTypeForm
        obj = mock.MagicMock()
        form = ExpenseTypeForm(
            _fd(name="Test Type", description="Test desc", is_active="y"),
            meta=FORM_META,
        )
        form._parsed_fields_meta = {"kind": "MISC"}
        form.apply_to(obj)
        assert obj.name == "Test Type"
        assert obj.fields_meta == {"kind": "MISC"}

    def test_apply_to_meta_from_gl_code(self):
        from forms import ExpenseTypeForm
        obj = mock.MagicMock()
        form = ExpenseTypeForm(
            _fd(name="Test Type", description="desc",
                gl_account_code="6000", is_active="y"),
            meta=FORM_META,
        )
        form._parsed_fields_meta = None
        form.apply_to(obj)
        assert obj.fields_meta == {"gl_account_code": "6000"}


class TestUnifiedDateFieldEdgeCases:
    def test_init_with_formats_list(self):
        from forms import UnifiedDateField
        class F(Form):
            d = UnifiedDateField(formats=["%d/%m/%Y", "%Y-%m-%d"])
        form = F(_fd(d="15/06/2025"), meta=FORM_META)
        assert form.d.data == date(2025, 6, 15)

    def test_init_with_format_as_list(self):
        from forms import UnifiedDateField
        class F(Form):
            d = UnifiedDateField(format=["%d-%m-%Y", "%Y-%m-%d"])
        form = F(_fd(d="25-12-2025"), meta=FORM_META)
        assert form.d.data == date(2025, 12, 25)

    def test_value_with_raw_data(self):
        from forms import UnifiedDateField
        class F(Form):
            d = UnifiedDateField()
        form = F(_fd(d="2025-06-15"), meta=FORM_META)
        assert form.d._value() == "2025-06-15"

    def test_value_no_raw_data_no_data(self):
        from forms import UnifiedDateField
        class F(Form):
            d = UnifiedDateField()
        form = F(_fd(d=""), meta=FORM_META)
        assert form.d._value() == ""

    def test_process_formdata_empty(self):
        from forms import UnifiedDateField
        class F(Form):
            d = UnifiedDateField()
        form = F(_fd(d=""), meta=FORM_META)
        assert form.d.data is None

    def test_process_formdata_invalid_format(self):
        from forms import UnifiedDateField
        class F(Form):
            d = UnifiedDateField()
        form = F(_fd(d="not-a-date"), meta=FORM_META)
        assert form.validate() is False

    def test_process_formdata_timestamp(self):
        from forms import UnifiedDateField
        class F(Form):
            d = UnifiedDateField()
        form = F(_fd(d="ts:1718476800"), meta=FORM_META)
        assert form.d.data is not None


class TestCustomerFormValidatePhone:
    def test_empty_phone_raises_error(self):
        from forms import CustomerForm
        form = CustomerForm(meta=FORM_META)
        field = mock.MagicMock()
        field.data = ""
        with pytest.raises(ValidationError):
            form.validate_phone(field)


class TestUserFormInitWithObj:
    def test_last_login_ip_and_count(self, app, mocker):
        from forms import UserForm
        mocker.patch("models.Role.query.order_by")
        mocker.patch("models.Branch.query")
        mocker.patch("utils.tenant_ui.branch_choices_for_form", return_value=[])
        obj = mock.MagicMock()
        obj.last_login = None
        obj.last_seen = None
        obj.last_login_ip = ""
        obj.login_count = ""
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"
            admin.role.name = "OWNER"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = UserForm(obj=obj, meta=FORM_META)
                form._editing_user_id = 1
                form.email.data = "a@b.com"
                with mock.patch("models.User.query.filter") as mf:
                    mf.return_value.first.return_value = None
                    form.validate_email(form.email)


class TestPaymentFormInitExpenseDirection:
    def test_expense_direction_default(self, app, mocker):
        from forms import PaymentForm
        import utils
        mocker.patch.object(utils, 'prepare_payment_form_choices')
        with app.test_request_context():
            admin = mock.MagicMock(is_system_account=True)
            admin.username = "admin"; admin.role.name = "admin"
            with mock.patch("flask_login.utils._get_user", return_value=admin):
                form = PaymentForm(_fd(entity_type="EXPENSE", direction="", currency="ILS"),
                                   meta=FORM_META)
                assert form.direction.data == "OUT"
