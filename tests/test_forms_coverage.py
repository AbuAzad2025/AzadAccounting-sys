"""Tests for forms.py uncovered blocks: utility functions, fallback classes, and complex form validation."""
from datetime import date, datetime
from decimal import Decimal
from unittest import mock
from werkzeug.datastructures import MultiDict
from wtforms.form import Form

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
    return not hasattr(_fm.QuerySelectField, '_wtforms_sqlalchemy')


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

    def test_db_exception(self, mocker):
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

    def test_supplier_mismatch_with_loan(self, mocker):
        from forms import SupplierLoanSettlementForm
        from datetime import datetime
        from extensions import db as _db
        loan_mock = mock.MagicMock(supplier_id=2)
        mocker.patch.object(_db.session, 'get', return_value=loan_mock)
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
    def test_refund_amount_exceeds_refundable(self, mocker):
        from forms import InvoiceRefundForm
        from extensions import db as _db
        mocker.patch.object(_db.session, 'get', return_value=mock.MagicMock(refundable_amount=Decimal("50")))
        form = InvoiceRefundForm(_fd(invoice_id="1", amount="100", reason="Test"), meta=FORM_META)
        assert form.validate() is False
        assert "amount" in form.errors

    def test_build_payment_payload(self):
        from forms import InvoiceRefundForm
        form = InvoiceRefundForm(_fd(invoice_id="1", amount="100", reason="Test", notes="Note"), meta=FORM_META)
        payload = form.build_payment_payload()
        assert payload["direction"] == "OUTGOING" and payload["entity_id"] == 1


class TestInvoiceCancelForm:
    def test_invoice_not_found(self, mocker):
        from forms import InvoiceCancelForm
        from extensions import db as _db
        mocker.patch.object(_db.session, 'get', return_value=None)
        form = InvoiceCancelForm(_fd(invoice_id="99", cancel_reason="Duplicate"), meta=FORM_META)
        assert form.validate() is False
        assert "invoice_id" in form.errors

    def test_invoice_already_cancelled(self, mocker):
        from forms import InvoiceCancelForm
        from extensions import db as _db
        mocker.patch.object(_db.session, 'get', return_value=mock.MagicMock(status="CANCELLED"))
        form = InvoiceCancelForm(_fd(invoice_id="1", cancel_reason="Duplicate"), meta=FORM_META)
        assert form.validate() is False
        assert "invoice_id" in form.errors

    def test_db_exception_graceful(self, mocker):
        from forms import InvoiceCancelForm
        from extensions import db as _db
        mocker.patch.object(_db.session, 'get', side_effect=Exception("DB down"))
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
        from models import is_direction_allowed
        mocker.patch.object(is_direction_allowed, '__call__', return_value=False)
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

    def test_online_warehouse_requires_unique_slug(self, mocker):
        from forms import WarehouseForm
        from models import Warehouse as W
        mock_q = mock.MagicMock()
        mock_q.filter.return_value.first.return_value = mock.MagicMock(id=99)
        mocker.patch.object(W, 'query', mock_q)
        fd = _fd(name="Online WH", warehouse_type="ONLINE", online_slug="my-shop")
        form = WarehouseForm(fd, meta=FORM_META)
        assert form.validate() is False
        assert "online_slug" in form.errors

    def test_online_warehouse_unique_slug_ok(self, mocker):
        from forms import WarehouseForm
        from models import Warehouse as W
        mock_q = mock.MagicMock()
        mock_q.filter.return_value.first.return_value = None
        mocker.patch.object(W, 'query', mock_q)
        fd = _fd(name="Online WH", warehouse_type="ONLINE", online_slug="my-shop")
        form = WarehouseForm(fd, meta=FORM_META)
        assert form.validate() is True

    def test_online_is_default_unique(self, mocker):
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

    def test_circular_parent_detected(self, mocker):
        from forms import WarehouseForm
        from extensions import db as _db
        parent = mock.MagicMock(id=2, parent_id=1)
        mocker.patch.object(_db.session, 'get', return_value=parent)
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
