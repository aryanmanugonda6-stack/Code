let categoryChartInstance = null;
let parsedCsvTransactions = [];

document.addEventListener("DOMContentLoaded", () => {
    const monthSelector = document.getElementById("monthSelector");
    
    // Initial Load
    refreshDashboard();

    // Month Selector Change
    monthSelector.addEventListener("change", () => {
        refreshDashboard();
    });

    // Form 1: Add Expense
    const addExpenseForm = document.getElementById("addExpenseForm");
    addExpenseForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const payload = {
            amount: parseFloat(document.getElementById("expAmount").value),
            category_id: parseInt(document.getElementById("expCategory").value),
            expense_date: document.getElementById("expDate").value,
            description: document.getElementById("expDesc").value,
        };

        try {
            const res = await fetch("/api/expenses", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                bootstrap.Modal.getInstance(document.getElementById("addExpenseModal")).hide();
                addExpenseForm.reset();
                refreshDashboard();
            } else {
                const err = await res.json();
                alert("Error saving expense: " + (err.error || "Unknown"));
            }
        } catch (e) {
            alert("Network error: " + e.message);
        }
    });

    // Form 2: Set Budget
    const budgetForm = document.getElementById("budgetForm");
    budgetForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const [year, month] = getSelectedYearMonth();
        const payload = {
            year: year,
            month: month,
            amount: parseFloat(document.getElementById("budgetAmountInput").value),
        };

        try {
            const res = await fetch("/api/budgets", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                bootstrap.Modal.getInstance(document.getElementById("budgetModal")).hide();
                refreshDashboard();
            } else {
                const err = await res.json();
                alert("Error setting budget: " + (err.error || "Unknown"));
            }
        } catch (e) {
            alert("Network error: " + e.message);
        }
    });

    // CSV Ingestion: File selection & Parse button
    const csvFileInput = document.getElementById("csvFileInput");
    const btnParseCsv = document.getElementById("btnParseCsv");
    csvFileInput.addEventListener("change", () => {
        btnParseCsv.disabled = !csvFileInput.files.length;
    });

    btnParseCsv.addEventListener("click", async () => {
        if (!csvFileInput.files.length) return;
        const formData = new FormData();
        formData.append("file", csvFileInput.files[0]);

        btnParseCsv.disabled = true;
        btnParseCsv.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Parsing...';

        try {
            const res = await fetch("/api/import/csv/preview", {
                method: "POST",
                body: formData
            });

            const data = await res.json();
            btnParseCsv.disabled = false;
            btnParseCsv.innerHTML = '<i class="bi bi-magic me-1"></i> Parse & Auto-Categorize';

            if (res.ok) {
                renderCsvPreview(data);
            } else {
                alert("Error: " + (data.error || "Failed to parse CSV"));
            }
        } catch (e) {
            btnParseCsv.disabled = false;
            btnParseCsv.innerHTML = '<i class="bi bi-magic me-1"></i> Parse & Auto-Categorize';
            alert("Network error: " + e.message);
        }
    });

    // CSV Ingestion: Confirm & Save
    const btnConfirmImport = document.getElementById("btnConfirmImport");
    btnConfirmImport.addEventListener("click", async () => {
        // Collect state from preview table
        const toImport = [];
        const rows = document.querySelectorAll("#previewTableBody tr");

        rows.forEach((tr, index) => {
            const chk = tr.querySelector(".csv-row-check");
            const catSelect = tr.querySelector(".csv-row-cat");
            const item = parsedCsvTransactions[index];

            if (chk && catSelect && item) {
                toImport.push({
                    date: item.date,
                    description: item.description,
                    amount: item.amount,
                    category_id: parseInt(catSelect.value),
                    import_hash: item.import_hash,
                    skip: !chk.checked
                });
            }
        });

        btnConfirmImport.disabled = true;
        btnConfirmImport.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Saving...';

        try {
            const res = await fetch("/api/import/csv/confirm", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ transactions: toImport })
            });

            const result = await res.json();
            btnConfirmImport.disabled = false;
            btnConfirmImport.innerHTML = '<i class="bi bi-check2-circle me-1"></i> Confirm & Save Transactions';

            if (res.ok) {
                alert(`Successfully imported ${result.imported_count} transactions!`);
                bootstrap.Modal.getInstance(document.getElementById("csvImportModal")).hide();
                // Reset CSV modal
                document.getElementById("csvPreviewSection").classList.add("d-none");
                btnConfirmImport.classList.add("d-none");
                csvFileInput.value = "";
                btnParseCsv.disabled = true;
                refreshDashboard();
            } else {
                alert("Error importing: " + (result.error || "Unknown"));
            }
        } catch (e) {
            btnConfirmImport.disabled = false;
            btnConfirmImport.innerHTML = '<i class="bi bi-check2-circle me-1"></i> Confirm & Save Transactions';
            alert("Network error: " + e.message);
        }
    });
});

function getSelectedYearMonth() {
    const val = document.getElementById("monthSelector").value; // 'YYYY-MM'
    const parts = val.split("-");
    return [parseInt(parts[0]), parseInt(parts[1])];
}

async function refreshDashboard() {
    const [year, month] = getSelectedYearMonth();
    await Promise.all([
        loadSummary(year, month),
        loadTransactions(year, month)
    ]);
}

async function loadSummary(year, month) {
    try {
        const res = await fetch(`/api/expenses/summary?year=${year}&month=${month}`);
        if (!res.ok) return;
        const data = await res.json();

        // 1. Update KPI Text
        document.getElementById("totalSpentText").innerText = `$${data.total_spent.toFixed(2)}`;
        document.getElementById("totalIncomeText").innerText = `$${data.total_income.toFixed(2)}`;
        document.getElementById("budgetRemainingText").innerText = `$${data.remaining_budget.toFixed(2)}`;
        document.getElementById("budgetLimitText").innerText = `$${data.budget_limit.toFixed(2)}`;
        document.getElementById("dailyBurnText").innerText = `$${data.safe_daily_spend.toFixed(2)}`;
        document.getElementById("daysLeftText").innerText = data.remaining_days;

        // 2. Budget Progress & Badges
        const progressBar = document.getElementById("budgetProgressBar");
        const percentBadge = document.getElementById("budgetPercentBadge");
        const statusNotice = document.getElementById("budgetStatusNotice");

        percentBadge.innerText = `${data.utilization_pct}% Used`;
        progressBar.style.width = `${Math.min(data.utilization_pct, 100)}%`;

        if (data.utilization_pct >= 100) {
            progressBar.className = "progress-bar bg-danger";
            percentBadge.className = "badge bg-danger bg-opacity-10 text-danger rounded-pill px-2";
            statusNotice.innerText = "Over Budget!";
            statusNotice.className = "text-danger fw-semibold";
        } else if (data.utilization_pct >= 80) {
            progressBar.className = "progress-bar bg-warning";
            percentBadge.className = "badge bg-warning bg-opacity-10 text-warning rounded-pill px-2";
            statusNotice.innerText = "Near Limit (≥80%)";
            statusNotice.className = "text-warning fw-semibold";
        } else {
            progressBar.className = "progress-bar bg-success";
            percentBadge.className = "badge bg-primary bg-opacity-10 text-primary rounded-pill px-2";
            statusNotice.innerText = "On Track";
            statusNotice.className = "text-muted";
        }

        // 3. Alert Banner
        const alertBanner = document.getElementById("alertBanner");
        if (data.alert_status !== "normal" && data.budget_limit > 0) {
            alertBanner.classList.remove("d-none");
            alertBanner.className = `alert alert-${data.alert_status === 'critical' ? 'danger' : 'warning'} shadow-sm rounded-4 mb-4`;
            document.getElementById("alertTitle").innerText = data.alert_status === 'critical' ? 'Critical Alert' : 'Spending Warning';
            document.getElementById("alertText").innerText = data.alert_message;
        } else {
            alertBanner.classList.add("d-none");
        }

        // 4. Prepopulate budget modal input with existing limit
        if (data.budget_limit > 0) {
            document.getElementById("budgetAmountInput").value = data.budget_limit;
        }

        // 5. Update Chart.js Doughnut
        renderChart(data.categories);

    } catch (e) {
        console.error("Failed to load summary:", e);
    }
}

async function loadTransactions(year, month) {
    try {
        const res = await fetch(`/api/expenses?year=${year}&month=${month}`);
        if (!res.ok) return;
        const expenses = await res.json();

        document.getElementById("txCountBadge").innerText = expenses.length;
        const tbody = document.getElementById("transactionsTableBody");
        tbody.innerHTML = "";

        if (expenses.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="text-center py-4 text-muted small">No transactions logged for this month.</td></tr>`;
            return;
        }

        expenses.forEach(e => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td class="small text-muted">${e.expense_date}</td>
                <td>
                    <div class="fw-semibold">${escapeHtml(e.description || "Expense")}</div>
                </td>
                <td>
                    <span class="badge rounded-pill px-2" style="background-color: ${e.category_color}; color: #fff;">
                        <i class="bi ${e.category_icon} me-1"></i> ${escapeHtml(e.category_name)}
                    </span>
                </td>
                <td class="text-end fw-bold text-dark">$${e.amount.toFixed(2)}</td>
                <td class="text-center">
                    <button class="btn btn-sm btn-link text-danger p-0 opacity-75" title="Delete" onclick="deleteTransaction(${e.id})">
                        <i class="bi bi-trash3"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });

    } catch (e) {
        console.error("Failed to load transactions:", e);
    }
}

async function deleteTransaction(id) {
    if (!confirm("Are you sure you want to delete this transaction?")) return;
    try {
        const res = await fetch(`/api/expenses/${id}`, { method: "DELETE" });
        if (res.ok) {
            refreshDashboard();
        } else {
            alert("Failed to delete transaction.");
        }
    } catch (e) {
        alert("Error: " + e.message);
    }
}

function renderChart(categories) {
    const ctx = document.getElementById("categoryChart").getContext("2d");
    const noDataDiv = document.getElementById("noDataChart");

    if (!categories || categories.length === 0) {
        if (categoryChartInstance) {
            categoryChartInstance.destroy();
            categoryChartInstance = null;
        }
        noDataDiv.classList.remove("d-none");
        return;
    }

    noDataDiv.classList.add("d-none");

    const labels = categories.map(c => c.name);
    const dataValues = categories.map(c => c.total);
    const bgColors = categories.map(c => c.color);

    if (categoryChartInstance) {
        categoryChartInstance.data.labels = labels;
        categoryChartInstance.data.datasets[0].data = dataValues;
        categoryChartInstance.data.datasets[0].backgroundColor = bgColors;
        categoryChartInstance.update();
    } else {
        categoryChartInstance = new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: labels,
                datasets: [{
                    data: dataValues,
                    backgroundColor: bgColors,
                    borderWidth: 2,
                    borderColor: "#ffffff"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: {
                            boxWidth: 12,
                            font: { family: "'Inter', sans-serif", size: 11 }
                        }
                    }
                },
                cutout: "65%"
            }
        });
    }
}

function renderCsvPreview(data) {
    parsedCsvTransactions = data.rows || [];
    const previewSection = document.getElementById("csvPreviewSection");
    const tbody = document.getElementById("previewTableBody");
    const btnConfirm = document.getElementById("btnConfirmImport");
    const badge = document.getElementById("previewSummaryBadge");

    badge.innerText = `${data.total_count} found (${data.duplicates_count} duplicates)`;
    tbody.innerHTML = "";

    if (parsedCsvTransactions.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">No valid rows detected.</td></tr>`;
        previewSection.classList.remove("d-none");
        btnConfirm.classList.add("d-none");
        return;
    }

    parsedCsvTransactions.forEach((row, i) => {
        const tr = document.createElement("tr");
        if (row.is_duplicate) {
            tr.className = "table-light opacity-75";
        }

        // Category dropdown options
        let catOptions = "";
        ALL_CATEGORIES.forEach(cat => {
            const selected = (cat.id === row.suggested_category_id) ? "selected" : "";
            catOptions += `<option value="${cat.id}" ${selected}>${cat.name}</option>`;
        });

        tr.innerHTML = `
            <td>
                <input type="checkbox" class="form-check-input csv-row-check" ${row.is_duplicate ? "" : "checked"}>
            </td>
            <td>${row.date}</td>
            <td>
                <span>${escapeHtml(row.description)}</span>
                ${row.is_duplicate ? '<span class="badge bg-warning text-dark ms-1">Existing</span>' : ''}
            </td>
            <td class="fw-bold">$${row.amount.toFixed(2)}</td>
            <td>
                <select class="form-select form-select-sm csv-row-cat" style="min-width: 150px;">
                    ${catOptions}
                </select>
            </td>
        `;
        tbody.appendChild(tr);
    });

    previewSection.classList.remove("d-none");
    btnConfirm.classList.remove("d-none");
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.innerText = text;
    return div.innerHTML;
}
