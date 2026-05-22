"""امتثال ضريبي — تسوية VAT وإقرار."""
from datetime import date, datetime

from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required

from permissions_config.enums import SystemPermissions
from utils import permission_required
from utils.vat_settlement_service import vat_settlement_for_period

tax_compliance_bp = Blueprint("tax_compliance_bp", __name__, url_prefix="/tax-compliance")


@tax_compliance_bp.route("/vat-settlement")
@login_required
@permission_required(SystemPermissions.MANAGE_TAX_COMPLIANCE)
def vat_settlement():
    start = request.args.get("start_date") or date.today().replace(day=1).isoformat()
    end = request.args.get("end_date") or date.today().isoformat()
    start_dt = datetime.combine(date.fromisoformat(start), datetime.min.time())
    end_dt = datetime.combine(date.fromisoformat(end), datetime.max.time())
    data = vat_settlement_for_period(start_dt, end_dt)
    if request.args.get("format") == "json":
        return jsonify({"success": True, "period": {"start": start, "end": end}, **data})
    return render_template(
        "tax_compliance/vat_settlement.html",
        start_date=start,
        end_date=end,
        data=data,
    )
