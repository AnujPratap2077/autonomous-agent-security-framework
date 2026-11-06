
const API_BASE = "/api";

let refreshInProgress = false;

const elements = {
    totalEvents: document.getElementById("total-events"),
    activeAgents: document.getElementById("active-agents"),
    totalAnomalies: document.getElementById("total-anomalies"),
    criticalRisks: document.getElementById("critical-risks"),

    activityTotal: document.getElementById("activity-total"),
    activitySuccess: document.getElementById("activity-success"),
    activityFailed: document.getElementById("activity-failed"),

    eventsTable: document.getElementById("events-table-body"),
    anomalyContainer: document.getElementById("anomaly-container"),
    activityChart: document.getElementById("activity-chart"),
    apiStatus: document.getElementById("api-status")
};

function updateText(element, value) {
    if (element) {
        element.textContent = value;
    }
}

async function fetchJSON(url) {
    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
    }

    return response.json();
}


// =========================================
// API CONNECTION STATUS
// =========================================

function updateAPIStatus(online) {
    if (!elements.apiStatus) return;

    const dot = elements.apiStatus.querySelector(".status-dot");
    const label = elements.apiStatus.querySelector("span:last-child");

    updateText(
        label,
        online ? "API CONNECTION ONLINE" : "API CONNECTION OFFLINE"
    );

    if (dot) {
        dot.style.background = online ? "#48d6a0" : "#f16b70";
        dot.style.boxShadow = online
            ? "0 0 10px rgba(72,214,160,0.6)"
            : "0 0 10px rgba(241,107,112,0.6)";
    }
}


// =========================================
// METRIC CARDS
// =========================================

function updateMetrics(summary, events, analyses) {
    updateText(elements.totalEvents, summary.total_events ?? 0);

    const uniqueAgents = new Set(
        events.map(event => event.agent_id)
    );

    updateText(elements.activeAgents, uniqueAgents.size);

    const totalAnomalies = analyses.reduce(
        (total, analysis) =>
            total + (analysis.anomalies?.length ?? 0),
        0
    );

    const criticalRisks = analyses.filter(
        analysis =>
            analysis.risk_assessment?.risk_level?.toLowerCase() === "critical"
    ).length;

    updateText(elements.totalAnomalies, totalAnomalies);
    updateText(elements.criticalRisks, criticalRisks);

    updateText(elements.activityTotal, summary.total_events ?? 0);
    updateText(elements.activitySuccess, summary.successful_events ?? 0);

    const unsuccessful =
        (summary.failed_events ?? 0) +
        (summary.blocked_events ?? 0);

    updateText(elements.activityFailed, unsuccessful);
}


// =========================================
// RECENT EVENTS TABLE
// =========================================

function updateEventsTable(events) {
    const table = elements.eventsTable;

    if (!table) return;

    table.replaceChildren();

    if (events.length === 0) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");

        cell.colSpan = 5;
        cell.className = "table-empty";
        cell.textContent = "No events received yet.";

        row.appendChild(cell);
        table.appendChild(row);
        return;
    }

    events.slice().reverse().slice(0, 10).forEach(event => {
        const row = document.createElement("tr");

        const values = [
            event.agent_id,
            event.action,
            event.tool_name || "—",
            event.status,
            new Date(event.timestamp).toLocaleString()
        ];

        values.forEach((value, index) => {
            const cell = document.createElement("td");
            cell.textContent = value ?? "—";

            if (index === 3) {
                const status = document.createElement("span");
                status.className = `event-status status-${event.status}`;
                status.textContent = value;
                cell.replaceChildren(status);
            }

            row.appendChild(cell);
        });

        table.appendChild(row);
    });
}


// =========================================
// ACTIVITY VISUALISATION
// =========================================

function updateActivityChart(events) {
    const chart = elements.activityChart;

    if (!chart) return;

    chart.replaceChildren();

    if (events.length === 0) {
        const empty = document.createElement("div");
        empty.className = "chart-empty";
        empty.innerHTML = `
            <div class="chart-empty-icon">⌁</div>
            <p>Awaiting telemetry data</p>
            <small>Activity visualisation will populate as events arrive</small>
        `;

        chart.appendChild(empty);
        return;
    }

    const grid = document.createElement("div");
    grid.className = "chart-grid-lines";

    for (let i = 0; i < 4; i++) {
        grid.appendChild(document.createElement("span"));
    }

    const barsContainer = document.createElement("div");
    barsContainer.className = "chart-bars";

    const recentEvents = events.slice(-20);

    const maxDuration = Math.max(
        ...recentEvents.map(event => Number(event.duration_ms) || 0),
        1
    );

    recentEvents.forEach(event => {
        const wrapper = document.createElement("div");
        wrapper.className = "activity-bar-wrapper";

        const bar = document.createElement("div");
        bar.className = `activity-bar bar-${event.status}`;

        const duration = Number(event.duration_ms) || 0;
        const height = Math.max(8, (duration / maxDuration) * 100);

        bar.style.height = `${height}%`;

        bar.title = `${event.action} | ${event.status} | ${duration} ms`;

        wrapper.appendChild(bar);
        barsContainer.appendChild(wrapper);
    });

    chart.append(grid, barsContainer);
}


// =========================================
// SESSION ANALYSIS
// =========================================

async function analyseSessions(events) {
    const sessions = new Map();

    events.forEach(event => {
        const key = JSON.stringify([
            event.agent_id,
            event.session_id
        ]);

        if (!sessions.has(key)) {
            sessions.set(key, {
                agent_id: event.agent_id,
                session_id: event.session_id
            });
        }
    });

    const results = await Promise.allSettled(
        [...sessions.values()].map(session => {
            const params = new URLSearchParams({
                agent_id: session.agent_id,
                session_id: session.session_id
            });

            return fetchJSON(`${API_BASE}/analyze?${params}`);
        })
    );

    return results
        .filter(result => result.status === "fulfilled")
        .map(result => result.value);
}


// =========================================
// RISK DISTRIBUTION
// =========================================

function updateRiskDistribution(analyses) {
    const levels = {
        low: 0,
        medium: 0,
        high: 0,
        critical: 0
    };

    analyses.forEach(analysis => {
        const level = analysis.risk_assessment?.risk_level?.toLowerCase();

        if (Object.prototype.hasOwnProperty.call(levels, level)) {
            levels[level]++;
        }
    });

    const total = analyses.length;

    Object.entries(levels).forEach(([level, count]) => {
        updateText(
            document.getElementById(`risk-${level}`),
            count
        );

        const bar = document.getElementById(`risk-${level}-bar`);

        if (bar) {
            const percentage = total > 0
                ? (count / total) * 100
                : 0;

            bar.style.width = `${percentage}%`;
        }
    });
}


// =========================================
// ANOMALY INTELLIGENCE
// =========================================

function updateAnomalies(analyses) {
    const container = elements.anomalyContainer;

    if (!container) return;

    container.replaceChildren();

    const findings = [];

    analyses.forEach(analysis => {
        (analysis.anomalies || []).forEach(anomaly => {
            findings.push({
                ...anomaly,
                agent_id: analysis.agent_id,
                session_id: analysis.session_id
            });
        });
    });

    if (findings.length === 0) {
        const empty = document.createElement("div");
        empty.className = "empty-state";

        const icon = document.createElement("div");
        icon.className = "empty-icon";
        icon.textContent = "⌬";

        const heading = document.createElement("p");
        heading.textContent = analyses.length
            ? "No anomalies detected"
            : "No analysis available";

        const description = document.createElement("small");
        description.textContent = analyses.length
            ? "No suspicious patterns were identified in the analysed sessions."
            : "Agent session analysis will appear here when events are received.";

        empty.append(icon, heading, description);
        container.appendChild(empty);
        return;
    }

    findings.slice(0, 6).forEach(anomaly => {
        const item = document.createElement("div");
        item.className = "anomaly-item";

        const top = document.createElement("div");
        top.className = "anomaly-item-top";

        const type = document.createElement("strong");
        type.textContent = (anomaly.type || "Unknown anomaly")
            .replaceAll("_", " ")
            .toUpperCase();

        const severity = document.createElement("span");
        severity.className =
            `anomaly-severity severity-${(anomaly.severity || "medium").toLowerCase()}`;
        severity.textContent = anomaly.severity || "Unknown";

        top.append(type, severity);

        const message = document.createElement("p");
        message.textContent = anomaly.message || "No description available.";

        const details = document.createElement("small");
        details.textContent =
            `AGENT: ${anomaly.agent_id} · SESSION: ${anomaly.session_id}`;

        item.append(top, message, details);
        container.appendChild(item);
    });
}


// =========================================
// MAIN DASHBOARD REFRESH
// =========================================

async function loadDashboard() {
    if (refreshInProgress) return;

    refreshInProgress = true;

    try {
        const [summary, events] = await Promise.all([
            fetchJSON(`${API_BASE}/summary`),
            fetchJSON(`${API_BASE}/events`)
        ]);

        updateAPIStatus(true);

        const analyses = await analyseSessions(events);

        updateMetrics(summary, events, analyses);
        updateEventsTable(events);
        updateActivityChart(events);
        updateRiskDistribution(analyses);
        updateAnomalies(analyses);

    } catch (error) {
        console.error("Dashboard loading error:", error);
        updateAPIStatus(false);

    } finally {
        refreshInProgress = false;
    }
}


// =========================================
// INITIAL LOAD AND AUTO REFRESH
// =========================================

loadDashboard();

setInterval(loadDashboard, 3000);
