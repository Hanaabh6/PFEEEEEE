(function () {
  function escapeHtml(value) {
    return String(value || "").replace(/[&<>\"']/g, function (ch) {
      if (ch === "&") return "&amp;";
      if (ch === "<") return "&lt;";
      if (ch === ">") return "&gt;";
      if (ch === "\"") return "&quot;";
      return "&#39;";
    });
  }

  function readReports() {
    try {
      var raw = localStorage.getItem("userReports");
      var parsed = raw ? JSON.parse(raw) : [];
      return Array.isArray(parsed) ? parsed : [];
    } catch (error) {
      return [];
    }
  }

  function writeReports(reports) {
    localStorage.setItem("userReports", JSON.stringify(reports));
  }

  function isAcceptedDecision(decision) {
    return String(decision || "").toLowerCase().indexOf("accept") >= 0;
  }

  function getApiBase() {
    if (!window.APP_CONFIG || !window.APP_CONFIG.API_BASE) return "";
    return String(window.APP_CONFIG.API_BASE).replace(/\/+$/, "");
  }

  function getAuthHeaders() {
    var headers = { "Content-Type": "application/json" };
    var token = String(localStorage.getItem("userToken") || "").trim();
    if (token) {
      headers.Authorization = "Bearer " + token;
    }
    return headers;
  }

  function hasActionableThing(report) {
    var thingId = String(report && report.id ? report.id : "").trim();
    return !!thingId && thingId.indexOf("general-report-") !== 0;
  }

  async function updateReportedThingStatus(report, status, maintenanceState) {
    var thingId = String(report && report.id ? report.id : "").trim();
    if (!thingId) {
      throw new Error("thing_id_missing");
    }

    var apiBase = getApiBase();
    if (!apiBase) {
      throw new Error("api_base_missing");
    }

    var response = await fetch(apiBase + "/things/" + encodeURIComponent(thingId) + "/status", {
      method: "PATCH",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        status: status,
        maintenance_state: typeof maintenanceState === "string" ? maintenanceState : ""
      })
    });

    if (!response.ok) {
      var payload = {};
      try {
        payload = await response.json();
      } catch (error) {
        payload = {};
      }
      throw new Error(payload && payload.detail ? payload.detail : "status_update_failed");
    }

    return response.json().catch(function () {
      return {};
    });
  }

  async function markReportedThingAsBroken(report) {
    return updateReportedThingStatus(report, "inactive", "en panne");
  }

  async function reactivateReportedThing(report) {
    return updateReportedThingStatus(report, "active", "");
  }

  function canReactivateReport(report) {
    var maintenanceState = String(
      report && (report.maintenanceState || report.maintenance_state)
        ? (report.maintenanceState || report.maintenance_state)
        : ""
    ).toLowerCase();
    var status = String(report && report.status ? report.status : "").toLowerCase();
    return maintenanceState.indexOf("panne") >= 0 || status.indexOf("objet en panne") >= 0;
  }

  function getStatusBadgeStyle(status) {
    var s = String(status || "").toLowerCase();
    if (s.indexOf("accept") >= 0 || s.indexOf("resolu") >= 0 || s.indexOf("trait") >= 0) {
      return "background:#dcfce7;color:#166534;";
    }
    if (s.indexOf("refus") >= 0 || s.indexOf("rej") >= 0) {
      return "background:#fee2e2;color:#b91c1c;";
    }
    return "background:#e2e8f0;color:#334155;";
  }

  function renderReportsHtml() {
    var reports = readReports();
    if (!reports.length) {
      return "<div class='p-2'><p style='margin:0;color:#475569;font-weight:600;'>Aucun signalement pour le moment.</p></div>";
    }

    var rows = reports.map(function (report, idx) {
      var name = escapeHtml(report && report.name ? report.name : "Objet non precise");
      var objectType = escapeHtml(report && report.objectType ? report.objectType : "");
      var position = escapeHtml(report && (report.location || report.position) ? (report.location || report.position) : "Position non definie");
      var type = escapeHtml(report && report.type ? report.type : "Non specifie");
      var desc = escapeHtml(report && report.description ? report.description : "Description non fournie");
      var status = escapeHtml(report && report.status ? report.status : "En attente");
      var reactivateButton = canReactivateReport(report)
        ? "<button type='button' onclick='window.adminReactivateReport(" + idx + ")' style='background:#d1fae5;color:#065f46;border:none;padding:6px 10px;border-radius:8px;cursor:pointer;font-size:12px;font-weight:700;'>Remettre en service</button>"
        : "";
      var acceptButton = "<button type='button' onclick='window.adminReviewReport(" + idx + ", \"Accepte\")' style='background:#dcfce7;color:#166534;border:none;padding:6px 10px;border-radius:8px;cursor:pointer;font-size:12px;font-weight:700;'>Accepter</button>";
      var rejectButton = "<button type='button' onclick='window.adminReviewReport(" + idx + ", \"Refuse\")' style='background:#fee2e2;color:#b91c1c;border:none;padding:6px 10px;border-radius:8px;cursor:pointer;font-size:12px;font-weight:700;'>Refuser</button>";
      var dateRaw = report && report.reportedAt ? report.reportedAt : "";
      var dateText = "-";
      if (dateRaw) {
        var d = new Date(dateRaw);
        dateText = Number.isNaN(d.getTime()) ? escapeHtml(dateRaw) : escapeHtml(d.toLocaleDateString("fr-FR"));
      }

      return "" +
        "<tr style='border-bottom:1px solid #e2e8f0;'>" +
        "<td style='padding:10px;color:#0f172a;font-weight:700;'>" + name + (objectType ? "<div style='margin-top:4px;font-size:12px;font-weight:600;color:#64748b;'>Type d'objet: " + objectType + "</div>" : "") + "</td>" +
        "<td style='padding:10px;color:#475569;'>" + position + "</td>" +
        "<td style='padding:10px;color:#475569;'>" + type + "</td>" +
        "<td style='padding:10px;color:#334155;max-width:360px;'>" + desc + "</td>" +
        "<td style='padding:10px;color:#64748b;white-space:nowrap;'>" + dateText + "</td>" +
        "<td style='padding:10px;'><span style='display:inline-block;padding:4px 8px;border-radius:999px;font-size:11px;font-weight:700;" + getStatusBadgeStyle(status) + "'>" + status + "</span></td>" +
        "<td style='padding:10px;'>" +
          "<div style='display:flex;gap:6px;flex-wrap:wrap;'>" +
            acceptButton +
            rejectButton +
            reactivateButton +
          "</div>" +
        "</td>" +
        "</tr>";
    }).join("");

    return "" +
      "<div class='p-2'>" +
        "<p style='margin:0 0 10px 0;color:#334155;font-weight:700;'>Demandes de signalement utilisateur</p>" +
        "<div style='overflow-x:auto;'>" +
          "<table style='width:100%;border-collapse:collapse;'>" +
            "<thead>" +
              "<tr style='border-bottom:1px solid #cbd5e1;'>" +
                "<th style='text-align:left;padding:10px;font-size:12px;color:#64748b;text-transform:uppercase;'>Objet</th>" +
                "<th style='text-align:left;padding:10px;font-size:12px;color:#64748b;text-transform:uppercase;'>Position</th>" +
                "<th style='text-align:left;padding:10px;font-size:12px;color:#64748b;text-transform:uppercase;'>Type</th>" +
                "<th style='text-align:left;padding:10px;font-size:12px;color:#64748b;text-transform:uppercase;'>Probleme</th>" +
                "<th style='text-align:left;padding:10px;font-size:12px;color:#64748b;text-transform:uppercase;'>Date</th>" +
                "<th style='text-align:left;padding:10px;font-size:12px;color:#64748b;text-transform:uppercase;'>Statut</th>" +
                "<th style='text-align:left;padding:10px;font-size:12px;color:#64748b;text-transform:uppercase;'>Action</th>" +
              "</tr>" +
            "</thead>" +
            "<tbody>" + rows + "</tbody>" +
          "</table>" +
        "</div>" +
      "</div>";
  }

  function openReportsOverlay() {
    if (typeof window.openOverlay === "function") {
      window.openOverlay("Signalements", renderReportsHtml());
      return;
    }

    var infoOverlay = document.getElementById("infoOverlay");
    var overlayTitle = document.getElementById("overlayTitle");
    var overlayBody = document.getElementById("overlayBody");
    if (!infoOverlay || !overlayTitle || !overlayBody) return;

    overlayTitle.textContent = "Signalements";
    overlayBody.innerHTML = renderReportsHtml();
    infoOverlay.hidden = false;
    infoOverlay.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  window.adminReviewReport = async function (index, decision) {
    var reports = readReports();
    var idx = Number(index);
    if (!Number.isFinite(idx) || idx < 0 || idx >= reports.length) return;

    try {
      if (isAcceptedDecision(decision)) {
        if (hasActionableThing(reports[idx])) {
          await markReportedThingAsBroken(reports[idx]);
          reports[idx].status = "Accepte - objet en panne";
          reports[idx].maintenanceState = "en panne";
          reports[idx].maintenance_state = "en panne";
        } else {
          reports[idx].status = "Accepte - signalement reçu";
        }
      } else {
        reports[idx].status = decision;
      }

      reports[idx].reviewedAt = new Date().toISOString();
      reports[idx].reviewedBy = "admin";
      writeReports(reports);
      openReportsOverlay();
    } catch (error) {
      console.error("Erreur traitement signalement:", error);
      if (typeof window.alert === "function") {
        window.alert("Impossible de mettre l'objet en panne pour le moment.");
      }
    }
  };

  window.adminReactivateReport = async function (index) {
    var reports = readReports();
    var idx = Number(index);
    if (!Number.isFinite(idx) || idx < 0 || idx >= reports.length) return;

    try {
      await reactivateReportedThing(reports[idx]);
      reports[idx].status = "Resolu - remis en service";
      reports[idx].maintenanceState = "";
      reports[idx].maintenance_state = "";
      reports[idx].reviewedAt = new Date().toISOString();
      reports[idx].reviewedBy = "admin";
      writeReports(reports);
      openReportsOverlay();
    } catch (error) {
      console.error("Erreur reactivation signalement:", error);
      if (typeof window.alert === "function") {
        window.alert("Impossible de rendre l'objet actif pour le moment.");
      }
    }
  };

  var trigger = document.getElementById("openAdminReportsOverlay");
  if (trigger) {
    trigger.addEventListener("click", function (event) {
      event.preventDefault();
      openReportsOverlay();
    });
  }
})();
