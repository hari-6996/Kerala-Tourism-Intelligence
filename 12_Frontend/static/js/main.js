/**
 * Kerala Tourism Intelligence — Client Interaction Engine
 */

let trendsChartInstance = null;

const HERITAGE_TICKERS = [
  "Vagamon's pine hills and rolling meadows host annual international paragliding gatherings in Idukki district.",
  "Munnar's high ranges are home to the Neelakurinji shrub, which blossoms across the shola slopes once every 12 years.",
  "Alappuzha's Punnamada Lake stages the Nehru Trophy Snake Boat Race each monsoon on the Vembanad backwaters.",
  "Kumarakom's Responsible Tourism initiatives model village-linked homestay and agrarian hospitality across Kottayam.",
  "Varkala preserves the only coastal tertiary sedimentary cliff formation rising directly above the Arabian Sea in southern Kerala.",
  "Bekal Fort in Kasaragod remains Kerala's largest 17th-century coastal rampart overlooking the Malabar shoreline."
];

let currentTickerIndex = 0;

document.addEventListener("DOMContentLoaded", function () {
  initHeritageTicker();
  initSearchAutocomplete();
});

function toggleSidebar(forceState) {
  const sidebar = document.getElementById("appSidebar");
  const backdrop = document.getElementById("sidebarBackdrop");
  if (!sidebar || !backdrop) return;

  const isOpen = typeof forceState === "boolean" ? forceState : !sidebar.classList.contains("open");
  sidebar.classList.toggle("open", isOpen);
  backdrop.classList.toggle("open", isOpen);
}

function initHeritageTicker() {
  const tickerEl = document.getElementById("heritage-ticker-text");
  if (!tickerEl) return;

  setInterval(() => {
    currentTickerIndex = (currentTickerIndex + 1) % HERITAGE_TICKERS.length;
    tickerEl.style.opacity = 0;
    setTimeout(() => {
      tickerEl.innerText = HERITAGE_TICKERS[currentTickerIndex];
      tickerEl.style.opacity = 1;
    }, 200);
  }, 7500);
}

function prevTicker() {
  const tickerEl = document.getElementById("heritage-ticker-text");
  if (!tickerEl) return;
  currentTickerIndex = (currentTickerIndex - 1 + HERITAGE_TICKERS.length) % HERITAGE_TICKERS.length;
  tickerEl.innerText = HERITAGE_TICKERS[currentTickerIndex];
}

function nextTicker() {
  const tickerEl = document.getElementById("heritage-ticker-text");
  if (!tickerEl) return;
  currentTickerIndex = (currentTickerIndex + 1) % HERITAGE_TICKERS.length;
  tickerEl.innerText = HERITAGE_TICKERS[currentTickerIndex];
}

function initSearchAutocomplete() {
  const input = document.getElementById("hero-search-input");
  if (!input) return;

  input.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      const val = input.value.trim();
      if (val) {
        window.location.href = `/destinations?search=${encodeURIComponent(val)}`;
      }
    }
  });
}

function filterRoster(category, btnEl) {
  document.querySelectorAll(".landscape-pill").forEach(el => el.classList.remove("active"));
  btnEl.classList.add("active");

  const items = document.querySelectorAll(".roster-btn");
  items.forEach(item => {
    const itemCat = item.getAttribute("data-category");
    item.style.display = (category === "All Destinations" || itemCat === category) ? "flex" : "none";
  });
}

async function selectDestination(destName, btnEl) {
  if (btnEl) {
    document.querySelectorAll(".roster-btn").forEach(el => el.classList.remove("active"));
    btnEl.classList.add("active");
  }

  const titleEl = document.getElementById("trend-dest-name");
  if (titleEl) titleEl.innerText = destName;

  const deepLinkEl = document.getElementById("trend-deepdive-link");
  if (deepLinkEl) {
    deepLinkEl.href = `/google-trends?destination=${encodeURIComponent(destName)}`;
  }

  const periodEl = document.getElementById("trend-period-select");
  const period = periodEl ? periodEl.value : "3y";

  try {
    const res = await fetch(`/api/trends/${encodeURIComponent(destName)}?period=${encodeURIComponent(period)}`);
    const data = await res.json();
    renderTrendsChart(destName, data.dates, data.scores);
  } catch (err) {
    console.error("Error loading trends:", err);
  }

  if (btnEl) {
    try {
      const dRes = await fetch(`/api/destination/${encodeURIComponent(destName)}`);
      const dData = await dRes.json();
      updateSpotlightCard(dData);
    } catch (err) {
      console.error("Error loading spotlight:", err);
    }
  }
}

function renderTrendsChart(destName, labels, values) {
  const ctx = document.getElementById("trendsChart");
  if (!ctx) return;

  if (trendsChartInstance) {
    trendsChartInstance.destroy();
  }

  const gradient = ctx.getContext("2d").createLinearGradient(0, 0, 0, 270);
  gradient.addColorStop(0, "rgba(21, 71, 52, 0.14)");
  gradient.addColorStop(1, "rgba(21, 71, 52, 0.0)");

  trendsChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Search Interest",
          data: values,
          borderColor: "#154734",
          backgroundColor: gradient,
          borderWidth: 2.25,
          tension: 0.35,
          fill: true,
          pointBackgroundColor: "#154734",
          pointBorderColor: "#ffffff",
          pointBorderWidth: 1.5,
          pointRadius: 3.5,
          pointHoverRadius: 5.5
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: "index",
        intersect: false
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: "#0d2a1d",
          titleColor: "#e6c973",
          bodyColor: "#ffffff",
          padding: 10,
          cornerRadius: 8,
          displayColors: false,
          callbacks: {
            label: function (context) {
              return `Interest Index: ${context.parsed.y} / 100`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            display: false
          },
          border: {
            display: false
          },
          ticks: {
            color: "#717e77",
            font: { family: "Plus Jakarta Sans", size: 11 },
            maxRotation: 0,
            autoSkip: true,
            maxTicksLimit: 7
          }
        },
        y: {
          min: 0,
          max: 100,
          border: {
            display: false,
            dash: [4, 4]
          },
          grid: {
            color: "#eceae2",
            tickLength: 0
          },
          ticks: {
            stepSize: 25,
            color: "#717e77",
            font: { family: "Plus Jakarta Sans", size: 11 },
            padding: 8
          }
        }
      }
    }
  });
}

function updateSpotlightCard(data) {
  const imgEl = document.getElementById("spotlight-img");
  const titleEl = document.getElementById("spotlight-title");
  const locEl = document.getElementById("spotlight-loc");
  const clusterPill = document.getElementById("spotlight-cluster-pill");
  const scoreEl = document.getElementById("spotlight-score");
  const ringEl = document.getElementById("spotlight-ring");
  const check1 = document.getElementById("spotlight-check1");
  const check2 = document.getElementById("spotlight-check2");
  const check3 = document.getElementById("spotlight-check3");
  const exploreBtn = document.getElementById("spotlight-explore-btn");

  if (imgEl) imgEl.src = data.Photo_URL;
  if (titleEl) titleEl.innerText = data.Destination;
  if (locEl) locEl.innerText = `${data.District} District · ${data.Tagline}`;
  if (clusterPill) clusterPill.innerText = `Cluster ${data.Cluster} · ${data.Cluster_Name}`;

  const oppScore = Math.max(0, Math.min(100, Number(data.Opportunity_Score) || 0));
  if (scoreEl) scoreEl.innerText = `${oppScore}%`;
  if (ringEl) {
    const circumference = 131.95;
    ringEl.style.strokeDashoffset = (circumference * (1 - oppScore / 100)).toFixed(2);
  }

  const growthNum = Number(data.Growth_2022_2024);
  const growthStr = `${growthNum >= 0 ? "+" : ""}${growthNum.toFixed(1)}%`;

  if (check1) check1.innerHTML = `<strong>Footfall (2024):</strong> ${Number(data.Total_Visitors_2024).toLocaleString()} visits`;
  if (check2) check2.innerHTML = `<strong>3-Year Growth:</strong> <span class="${growthNum >= 0 ? 'growth-pos' : 'growth-neg'}">${growthStr}</span>`;
  if (check3) check3.innerHTML = `<strong>Suggested Venture:</strong> ${data.Primary_Concept || data.Recommended_Business}`;

  if (exploreBtn) exploreBtn.href = `/destinations?highlight=${encodeURIComponent(data.Destination)}`;
}
