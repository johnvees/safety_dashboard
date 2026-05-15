<template>
  <div class="dash">
    <!-- Header -->
    <div class="dash-header">
      <div>
        <h2>Dashboard Overview</h2>
        <p class="dash-sub">K3L Safety inspection summary &middot; {{ currentMonthYear }}</p>
      </div>
      <div class="welcome-pill">
        <span class="welcome-dot"></span>
        {{ greeting }}, <strong>{{ userName }}</strong>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <span>Memuat data dashboard…</span>
    </div>

    <!-- Error state -->
    <div v-else-if="loadFailed" class="dashboard-empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="1.5" width="48" height="48">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
      <h3>Tidak dapat memuat data</h3>
      <p>Pastikan server backend sudah berjalan, lalu refresh halaman ini.</p>
      <button class="empty-btn" @click="() => window.location.reload()">Refresh</button>
    </div>

    <!-- Empty state -->
    <div v-else-if="records.length === 0" class="dashboard-empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5" width="48" height="48">
        <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>
        <rect x="9" y="3" width="6" height="4" rx="1"/>
        <line x1="9" y1="12" x2="15" y2="12"/>
        <line x1="9" y1="16" x2="13" y2="16"/>
      </svg>
      <h3>Belum ada data temuan</h3>
      <p>Data Inspection K3L belum tersedia. Mulai dengan menambahkan temuan pertama.</p>
      <button class="empty-btn" @click="() => $router.push('/dashboard/reports/inspection-k3l')">+ Tambah Temuan</button>
    </div>

    <template v-else>
      <!-- Date filter row -->
      <div class="date-filter-row">
        <button v-for="opt in DATE_PRESETS" :key="opt.value" class="date-chip" :class="{ active: filterDate === opt.value }" @click="setDatePreset(opt.value)">{{ opt.label }}</button>
        <template v-if="filterDate === 'custom'">
          <label class="toolbar-date-wrap">
            <input type="date" v-model="customDateFrom" class="toolbar-date" @click="$event.target.showPicker?.()" />
          </label>
          <span class="date-sep">–</span>
          <label class="toolbar-date-wrap">
            <input type="date" v-model="customDateTo" class="toolbar-date" @click="$event.target.showPicker?.()" />
          </label>
        </template>
      </div>

      <!-- KPI Cards -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-icon-wrap" style="background:#eff6ff">
            <svg viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" width="22" height="22">
              <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>
              <rect x="9" y="3" width="6" height="4" rx="1"/>
              <line x1="9" y1="12" x2="15" y2="12"/>
              <line x1="9" y1="16" x2="13" y2="16"/>
            </svg>
          </div>
          <div class="kpi-body">
            <div class="kpi-value">{{ stats.total }}</div>
            <div class="kpi-label">Total Reports</div>
            <div class="kpi-meta">All time</div>
          </div>
          <div class="kpi-bar" style="background:#3b82f6"></div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon-wrap" style="background:#fffbeb">
            <svg viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" width="22" height="22">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          </div>
          <div class="kpi-body">
            <div class="kpi-value">{{ stats.open }}</div>
            <div class="kpi-label">Open</div>
            <div class="kpi-meta">Needs attention</div>
          </div>
          <div class="kpi-bar" style="background:#f59e0b"></div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon-wrap" style="background:#eef2ff">
            <svg viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" width="22" height="22">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
          </div>
          <div class="kpi-body">
            <div class="kpi-value">{{ stats.inProgress }}</div>
            <div class="kpi-label">In Progress</div>
            <div class="kpi-meta">Being resolved</div>
          </div>
          <div class="kpi-bar" style="background:#6366f1"></div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon-wrap" style="background:#f0fdf4">
            <svg viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" width="22" height="22">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <div class="kpi-body">
            <div class="kpi-value">{{ stats.closed }}</div>
            <div class="kpi-label">Resolved</div>
            <div class="kpi-meta">Closed reports</div>
          </div>
          <div class="kpi-bar" style="background:#10b981"></div>
        </div>
      </div>

      <!-- Resolution rate bar -->
      <div class="rate-card" v-if="stats.total > 0">
        <div class="rate-label">
          <span>Resolution Rate</span>
          <strong>{{ resolutionRate }}%</strong>
        </div>
        <div class="rate-track">
          <div class="rate-fill" :style="{ width: resolutionRate + '%' }"></div>
        </div>
        <div class="rate-breakdown">
          <span class="rb-open">{{ stats.open }} Open</span>
          <span class="rb-progress">{{ stats.inProgress }} In Progress</span>
          <span class="rb-closed">{{ stats.closed }} Closed</span>
        </div>
      </div>

      <!-- Charts row -->
      <div class="charts-row">
        <!-- Monthly grouped bar chart -->
        <div class="chart-card chart-wide">
          <div class="chart-header">
            <div>
              <div class="chart-title">Monthly Trend</div>
              <div class="chart-subtitle">Reports by category per month (last 6 months)</div>
            </div>
            <div class="grouped-legend">
              <span v-for="s in activeCategories" :key="s.label" class="gl-item">
                <span class="gl-dot" :style="{ background: s.color }"></span>{{ s.label }}
              </span>
            </div>
          </div>
          <div class="chart-body chart-grouped-wrap">
            <div class="bar-scroll-outer" ref="barScrollRef" @mousemove="onChartMouseMove" @mouseleave="hideTooltip">
            <svg viewBox="0 0 520 185" class="bar-svg" xmlns="http://www.w3.org/2000/svg">
              <!-- Horizontal grid lines -->
              <line v-for="gl in gridLines" :key="gl.y"
                x1="44" :y1="gl.y" x2="512" :y2="gl.y"
                stroke="#f1f5f9" stroke-width="1.5"/>
              <!-- Y-axis labels -->
              <text v-for="gl in gridLines" :key="`y${gl.y}`"
                x="38" :y="gl.y + 4"
                text-anchor="end" font-size="10" fill="#94a3b8">{{ gl.label }}</text>
              <!-- Groups -->
              <g
                v-for="(grp, i) in groupedBarData" :key="i"
                @mouseenter="showGroupTooltip(grp)"
                @mouseleave="hideTooltip"
                style="cursor:default"
              >
                <!-- hover hit area -->
                <rect
                  :x="grp.bars[0].x - 4"
                  y="0"
                  :width="grp.groupW + 8"
                  height="165"
                  fill="transparent"
                />
                <rect
                  v-for="(bar, j) in grp.bars" :key="j"
                  :x="bar.x" :y="bar.y" :width="bar.w" :height="Math.max(bar.h, 2)"
                  rx="4"
                  :fill="bar.color"
                  :opacity="tooltipData && tooltipData.label !== grp.label ? 0.4 : 1"
                  style="transition: opacity 0.15s"
                />
                <!-- Total above group -->
                <text v-if="grp.total > 0"
                  :x="grp.labelX" :y="grp.topY"
                  text-anchor="middle" font-size="11" font-weight="700" fill="#475569">
                  {{ grp.total }}
                </text>
                <!-- Month label -->
                <text
                  :x="grp.labelX" :y="178"
                  text-anchor="middle" font-size="11" fill="#64748b">
                  {{ grp.label }}
                </text>
              </g>
            </svg>
            <!-- Tooltip -->
            <div
              v-if="tooltipData"
              class="bar-tooltip"
              :style="{ left: tooltipPos.x + 'px', top: tooltipPos.y + 'px' }"
            >
              <div class="tt-month">{{ tooltipData.label }}</div>
              <div v-for="s in activeCategories" :key="s.key" class="tt-row">
                <span class="tt-dot" :style="{ background: s.color }"></span>
                <span class="tt-label">{{ s.label }}</span>
                <span class="tt-val">{{ tooltipData[s.key] }}</span>
              </div>
            </div>
            </div><!-- end bar-scroll-outer -->
          </div>
        </div>

        <!-- Donut chart -->
        <div class="chart-card chart-narrow">
          <div class="chart-header">
            <div>
              <div class="chart-title">By Category</div>
              <div class="chart-subtitle">Finding distribution</div>
            </div>
          </div>
          <div class="donut-body" @mousemove="onDonutMouseMove" @mouseleave="hideDonutTooltip">
            <svg viewBox="0 0 200 200" class="donut-svg" xmlns="http://www.w3.org/2000/svg">
              <circle cx="100" cy="100" r="65" fill="none" stroke="#f1f5f9" stroke-width="30"/>
              <circle
                v-for="seg in donutSegments" :key="seg.category"
                cx="100" cy="100" r="65"
                fill="none"
                :stroke="seg.color"
                stroke-width="30"
                :stroke-dasharray="`${seg.length} ${seg.gap}`"
                :stroke-dashoffset="-seg.offset"
                transform="rotate(-90 100 100)"
                stroke-linecap="butt"
                :opacity="hoveredDonut && hoveredDonut.category !== seg.category ? 0.3 : 1"
                style="transition: opacity 0.15s; cursor: pointer"
                @mouseenter="hoveredDonut = seg"
                @mouseleave="hoveredDonut = null"
              />
              <text x="100" y="95" text-anchor="middle" font-size="26" font-weight="800" fill="#1e293b">{{ stats.total }}</text>
              <text x="100" y="113" text-anchor="middle" font-size="10" fill="#94a3b8" letter-spacing="1">REPORTS</text>
            </svg>
            <div
              v-if="hoveredDonut"
              class="donut-tooltip"
              :style="{ left: donutTooltipPos.x + 'px', top: donutTooltipPos.y + 'px' }"
            >
              <span class="dt-dot" :style="{ background: hoveredDonut.color }"></span>
              <span class="dt-cat">{{ hoveredDonut.category }}</span>
              <span class="dt-count">{{ hoveredDonut.count }}</span>
              <span class="dt-pct">{{ stats.total ? Math.round(hoveredDonut.count / stats.total * 100) : 0 }}%</span>
            </div>
            <div class="donut-legend">
              <div v-for="seg in donutSegments" :key="seg.category" class="legend-item">
                <span class="legend-dot" :style="{ background: seg.color }"></span>
                <span class="legend-label">{{ seg.category }}</span>
                <span class="legend-count">{{ seg.count }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom row: Calendar + Recent reports -->
      <div class="bottom-row">
        <!-- Calendar -->
        <div class="chart-card">
          <div class="chart-header">
            <div>
              <div class="chart-title">Activity Calendar</div>
              <div class="chart-subtitle">{{ calendarMonthYear }}</div>
            </div>
            <div class="cal-nav">
              <button class="cal-btn" @click="prevMonth">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <polyline points="15 18 9 12 15 6"/>
                </svg>
              </button>
              <button class="cal-btn" @click="nextMonth">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <polyline points="9 18 15 12 9 6"/>
                </svg>
              </button>
            </div>
          </div>
          <div class="cal-body" @mousemove="onCalMouseMove" @mouseleave="hoveredDay = null">
            <div class="cal-weekdays">
              <div v-for="d in ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']" :key="d" class="cal-wd">{{ d }}</div>
            </div>
            <div class="cal-grid">
              <div
                v-for="(day, i) in calendarDays" :key="i"
                class="cal-day"
                :class="{
                  'cal-other': !day.currentMonth,
                  'cal-today': day.isToday,
                  'cal-active': day.currentMonth && day.count > 0,
                }"
                @mouseenter="day.currentMonth && day.count > 0 ? hoveredDay = day : null"
                @mouseleave="hoveredDay = null"
              >
                <span class="cal-num">{{ day.date }}</span>
                <span v-if="day.count > 0 && day.currentMonth" class="cal-badge">{{ day.count }}</span>
              </div>
            </div>
            <!-- Day tooltip -->
            <div
              v-if="hoveredDay"
              class="cal-tooltip"
              :style="{ left: dayTooltipPos.x + 'px', top: dayTooltipPos.y + 'px' }"
            >
              <div class="cal-tt-date">{{ calendarMonthYear.split(' ')[0] }} {{ hoveredDay.date }}</div>
              <div class="cal-tt-total">{{ hoveredDay.count }} report{{ hoveredDay.count !== 1 ? 's' : '' }}</div>
              <div v-for="(cnt, cat) in hoveredDay.cats" :key="cat" class="cal-tt-row">
                <span class="cal-tt-dot" :style="{ background: categoryColor(cat) }"></span>
                <span class="cal-tt-cat">{{ cat }}</span>
                <span class="cal-tt-cnt">{{ cnt }}</span>
              </div>
            </div>
          </div>
          <!-- Calendar legend -->
          <div class="cal-legend">
            <span class="cal-leg-item"><span class="cal-leg-dot" style="background:#3b82f6"></span> Has reports</span>
            <span class="cal-leg-item"><span class="cal-leg-today"></span> Today</span>
          </div>
        </div>

        <!-- Recent reports -->
        <div class="chart-card">
          <div class="chart-header">
            <div>
              <div class="chart-title">Recent Reports</div>
              <div class="chart-subtitle">Latest K3L findings</div>
            </div>
            <router-link to="/dashboard/reports/inspection-k3l" class="view-all-link">
              View all
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><polyline points="9 18 15 12 9 6"/></svg>
            </router-link>
          </div>
          <div class="recent-list">
            <div v-if="recentRecords.length === 0" class="empty-recent">
              <svg viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.5" width="40" height="40">
                <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>
                <rect x="9" y="3" width="6" height="4" rx="1"/>
              </svg>
              <p>No reports yet</p>
            </div>
            <div v-for="rec in recentRecords" :key="rec.id" class="recent-item" @click="openRecord(rec.id)" style="cursor:pointer">
              <div class="recent-cat-dot" :style="{ background: categoryColor(rec.kategoriTemuan) }"></div>
              <div class="recent-info">
                <div class="recent-cat">{{ rec.kategoriTemuan }}</div>
                <div class="recent-loc">{{ rec.lokasi || 'No location specified' }}</div>
              </div>
              <div class="recent-right">
                <span :class="['status-chip', `sc-${rec.status.toLowerCase().replace(' ', '-')}`]">{{ rec.status }}</span>
                <span class="recent-date">{{ formatDate(rec.tanggal) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { inspectionK3LService } from '@/services/inspectionK3LService.js';
import { authService } from '@/services/authService.js';

const router = useRouter();

const records = ref([]);
const loading = ref(true);
const loadFailed = ref(false);
const calendarDate = ref(new Date());
const barScrollRef = ref(null);

const filterDate = ref('all');
const customDateFrom = ref('');
const customDateTo = ref('');

const DATE_PRESETS = [
  { label: 'Semua', value: 'all' },
  { label: 'Hari ini', value: 'today' },
  { label: 'Minggu ini', value: 'week' },
  { label: 'Bulan ini', value: 'month' },
  { label: 'Kustom', value: 'custom' },
];

function setDatePreset(val) {
  filterDate.value = val;
  if (val !== 'custom') { customDateFrom.value = ''; customDateTo.value = ''; }
}

const filteredByDate = computed(() => {
  if (filterDate.value === 'all') return records.value;
  const today = new Date(); today.setHours(0, 0, 0, 0);
  return records.value.filter(r => {
    if (!r.tanggal) return false;
    const d = new Date(r.tanggal); d.setHours(0, 0, 0, 0);
    if (filterDate.value === 'today') return d.getTime() === today.getTime();
    if (filterDate.value === 'week') {
      const start = new Date(today); start.setDate(today.getDate() - today.getDay());
      const end = new Date(start); end.setDate(start.getDate() + 6);
      return d >= start && d <= end;
    }
    if (filterDate.value === 'month') return d.getMonth() === today.getMonth() && d.getFullYear() === today.getFullYear();
    if (filterDate.value === 'custom') {
      if (customDateFrom.value) { const from = new Date(customDateFrom.value); from.setHours(0,0,0,0); if (d < from) return false; }
      if (customDateTo.value)   { const to   = new Date(customDateTo.value);   to.setHours(0,0,0,0);   if (d > to)   return false; }
    }
    return true;
  });
});

const user = authService.getCurrentUser();
const userName = computed(() => {
  if (user?.fullName) return user.fullName.split(' ')[0];
  if (user?.username) return user.username;
  return (user?.email || '').split('@')[0] || 'there';
});

const greeting = computed(() => {
  const h = new Date().getHours();
  if (h < 12) return 'Good morning';
  if (h < 18) return 'Good afternoon';
  return 'Good evening';
});

const currentMonthYear = computed(() =>
  new Date().toLocaleString('default', { month: 'long', year: 'numeric' })
);

// ── Stats ──────────────────────────────────────────────────────────
const stats = computed(() => ({
  total: filteredByDate.value.length,
  open: filteredByDate.value.filter(r => r.status === 'Open').length,
  inProgress: filteredByDate.value.filter(r => r.status === 'In Progress').length,
  closed: filteredByDate.value.filter(r => r.status === 'Closed').length,
}));

const resolutionRate = computed(() => {
  if (!stats.value.total) return 0;
  return Math.round((stats.value.closed / stats.value.total) * 100);
});

// ── Grouped bar chart (by category) ───────────────────────────────
const CAT_COLORS = {
  'Low':    '#4ade80',
  'Medium': '#fbbf24',
  'High':   '#f87171',
};

const activeCategories = computed(() => {
  const seen = new Set(records.value.map(r => r.kategoriTemuan).filter(Boolean));
  const ordered = Object.keys(CAT_COLORS).filter(c => seen.has(c));
  seen.forEach(c => { if (!CAT_COLORS[c]) ordered.push(c); });
  return ordered.map(cat => ({ key: cat, label: cat, color: CAT_COLORS[cat] || '#94a3b8' }));
});

const monthlyData = computed(() => {
  const now = new Date();
  const cats = activeCategories.value;
  const months = Array.from({ length: 6 }, (_, i) => {
    const d = new Date(now.getFullYear(), now.getMonth() - (5 - i), 1);
    const counts = {};
    cats.forEach(c => { counts[c.key] = 0; });
    return { label: d.toLocaleString('default', { month: 'short' }), year: d.getFullYear(), month: d.getMonth(), counts };
  });
  records.value.forEach(r => {
    if (!r.tanggal || !r.kategoriTemuan) return;
    const d = new Date(r.tanggal);
    const idx = months.findIndex(m => m.year === d.getFullYear() && m.month === d.getMonth());
    if (idx >= 0 && months[idx].counts[r.kategoriTemuan] !== undefined) {
      months[idx].counts[r.kategoriTemuan]++;
    }
  });
  return months;
});

const CHART_TOP = 30;
const CHART_H = 140;
const CHART_LEFT = 48;

const barLayout = computed(() => {
  const n = Math.max(1, activeCategories.value.length);
  const plotW = 464; // 520 - CHART_LEFT - 8
  const groupGap = 16;
  const groupW = Math.floor((plotW - 5 * groupGap) / 6);
  const barInnerGap = n > 1 ? 2 : 0;
  const barW = Math.max(4, Math.floor((groupW - (n - 1) * barInnerGap) / n));
  const actualGroupW = n * barW + (n - 1) * barInnerGap;
  return { barW, barInnerGap, groupGap, groupW: actualGroupW };
});

const groupedBarData = computed(() => {
  const data = monthlyData.value;
  const cats = activeCategories.value;
  const { barW, barInnerGap, groupGap, groupW } = barLayout.value;
  const maxVal = Math.max(...data.flatMap(d => cats.map(c => d.counts[c.key] || 0)), 1);
  return data.map((d, i) => {
    const gx = CHART_LEFT + i * (groupW + groupGap);
    const bars = cats.map((c, j) => {
      const count = d.counts[c.key] || 0;
      const h = (count / maxVal) * CHART_H;
      return { x: gx + j * (barW + barInnerGap), y: CHART_TOP + CHART_H - h, w: barW, h, count, color: c.color };
    });
    const total = cats.reduce((s, c) => s + (d.counts[c.key] || 0), 0);
    const topY = Math.min(...bars.map(b => b.y)) - 8;
    const catCounts = {};
    cats.forEach(c => { catCounts[c.key] = d.counts[c.key] || 0; });
    return { bars, label: d.label, labelX: gx + groupW / 2, groupW, total, topY, ...catCounts };
  });
});

const gridLines = computed(() => {
  const cats = activeCategories.value;
  const maxVal = Math.max(...monthlyData.value.flatMap(d => cats.map(c => d.counts[c.key] || 0)), 1);
  const step = maxVal <= 4 ? 1 : Math.ceil(maxVal / 4);
  const ticks = [];
  for (let v = 0; v <= maxVal; v += step) {
    ticks.push({ y: CHART_TOP + CHART_H - (v / maxVal) * CHART_H, label: v });
  }
  if (ticks[ticks.length - 1].label !== maxVal) {
    ticks.push({ y: CHART_TOP, label: maxVal });
  }
  return ticks;
});

// ── Tooltip ────────────────────────────────────────────────────────
const tooltipData = ref(null);
const tooltipPos  = ref({ x: 0, y: 0 });

function showGroupTooltip(grp) {
  tooltipData.value = grp;
}
function hideTooltip() {
  tooltipData.value = null;
}
function onChartMouseMove(e) {
  const rect = e.currentTarget.getBoundingClientRect();
  const TT_W = 155;
  let x = e.clientX - rect.left + 14;
  let y = e.clientY - rect.top - 65;
  if (x + TT_W > rect.width) x = e.clientX - rect.left - TT_W - 14;
  if (y < 4) y = 4;
  tooltipPos.value = { x, y };
}

// ── Donut chart ────────────────────────────────────────────────────
const hoveredDonut = ref(null);
const donutTooltipPos = ref({ x: 0, y: 0 });

function onDonutMouseMove(e) {
  const rect = e.currentTarget.getBoundingClientRect();
  donutTooltipPos.value = {
    x: e.clientX - rect.left + 12,
    y: e.clientY - rect.top - 44,
  };
}

function hideDonutTooltip() {
  hoveredDonut.value = null;
}

function categoryColor(cat) {
  return CAT_COLORS[cat] || '#94a3b8';
}

const CIRC = 2 * Math.PI * 65;

const donutSegments = computed(() => {
  if (!stats.value.total) return [];
  const counts = {};
  records.value.forEach(r => { counts[r.kategoriTemuan] = (counts[r.kategoriTemuan] || 0) + 1; });
  let cumulative = 0;
  const order = Object.keys(CAT_COLORS);
  return Object.entries(counts)
    .sort((a, b) => {
      const ai = order.indexOf(a[0]);
      const bi = order.indexOf(b[0]);
      return (ai === -1 ? 999 : ai) - (bi === -1 ? 999 : bi);
    })
    .map(([cat, count]) => {
      const fullLen = (count / stats.value.total) * CIRC;
      const seg = {
        category: cat,
        count,
        color: CAT_COLORS[cat] || '#94a3b8',
        length: Math.max(fullLen - 2, 0),
        gap: CIRC - Math.max(fullLen - 2, 0),
        offset: cumulative,
      };
      cumulative += fullLen;
      return seg;
    });
});

// ── Calendar ───────────────────────────────────────────────────────
const hoveredDay = ref(null);
const dayTooltipPos = ref({ x: 0, y: 0 });

function onCalMouseMove(e) {
  const rect = e.currentTarget.getBoundingClientRect();
  const TT_W = 150;
  let x = e.clientX - rect.left + 12;
  let y = e.clientY - rect.top - 60;
  if (x + TT_W > rect.width) x = e.clientX - rect.left - TT_W - 12;
  if (y < 4) y = 4;
  dayTooltipPos.value = { x, y };
}
const calendarMonthYear = computed(() =>
  calendarDate.value.toLocaleString('default', { month: 'long', year: 'numeric' })
);

const calendarDays = computed(() => {
  const year = calendarDate.value.getFullYear();
  const month = calendarDate.value.getMonth();
  const today = new Date();

  const firstDow = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const daysInPrev = new Date(year, month, 0).getDate();

  const reportMap = {};
  records.value.forEach(r => {
    if (!r.tanggal) return;
    const d = new Date(r.tanggal + 'T00:00:00');
    if (d.getFullYear() === year && d.getMonth() === month) {
      const key = d.getDate();
      if (!reportMap[key]) reportMap[key] = { count: 0, cats: {} };
      reportMap[key].count++;
      if (r.kategoriTemuan) reportMap[key].cats[r.kategoriTemuan] = (reportMap[key].cats[r.kategoriTemuan] || 0) + 1;
    }
  });

  const days = [];
  for (let i = firstDow - 1; i >= 0; i--) days.push({ date: daysInPrev - i, currentMonth: false, isToday: false, count: 0, cats: {} });
  for (let d = 1; d <= daysInMonth; d++) {
    const isToday = d === today.getDate() && month === today.getMonth() && year === today.getFullYear();
    days.push({ date: d, currentMonth: true, isToday, count: reportMap[d]?.count || 0, cats: reportMap[d]?.cats || {} });
  }
  for (let d = 1; days.length < 42; d++) days.push({ date: d, currentMonth: false, isToday: false, count: 0, cats: {} });
  return days;
});

function prevMonth() {
  const d = new Date(calendarDate.value);
  d.setMonth(d.getMonth() - 1);
  calendarDate.value = d;
}
function nextMonth() {
  const d = new Date(calendarDate.value);
  d.setMonth(d.getMonth() + 1);
  calendarDate.value = d;
}

// ── Recent records ─────────────────────────────────────────────────
const recentRecords = computed(() =>
  [...filteredByDate.value]
    .sort((a, b) => new Date(b.createdAt || 0) - new Date(a.createdAt || 0))
    .slice(0, 6)
);

function openRecord(id) {
  router.push({ path: '/dashboard/reports/inspection-k3l', query: { view: id } });
}

function formatDate(s) {
  if (!s) return '—';
  return new Date(s + 'T00:00:00').toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
}

onMounted(async () => {
  const timeout = setTimeout(() => {
    loading.value = false;
    loadFailed.value = true;
  }, 10000);
  try {
    records.value = await inspectionK3LService.list();
  } catch (e) {
    console.error(e);
    loadFailed.value = true;
  } finally {
    clearTimeout(timeout);
    loading.value = false;
    await nextTick();
    if (barScrollRef.value) {
      barScrollRef.value.scrollLeft = barScrollRef.value.scrollWidth;
    }
  }
});
</script>

<style scoped>
.dash {
  padding: 28px 32px;
  max-width: 1400px;
}

/* ── Date filter ─────────────────────────────────────────────────── */
.date-filter-row { display: flex; align-items: center; gap: 6px; margin-bottom: 20px; flex-wrap: wrap; }
.date-chip { background: #f1f5f9; border: 1px solid transparent; border-radius: 20px; padding: 5px 14px; font-size: 13px; color: #64748b; cursor: pointer; transition: all 0.15s; white-space: nowrap; }
.date-chip:hover { background: #e2e8f0; color: #1e293b; }
.date-chip.active { background: #3b82f6; color: #fff; border-color: #3b82f6; }
.toolbar-date-wrap { display: inline-flex; border: 1px solid #cbd5e1; border-radius: 8px; background: #fff; overflow: hidden; cursor: pointer; transition: border-color 0.15s; }
.toolbar-date-wrap:focus-within { border-color: #3b82f6; }
.toolbar-date { border: none; background: transparent; color: #1e293b; font-size: 13px; padding: 6px 10px; outline: none; cursor: pointer; color-scheme: light; width: 140px; }
.date-sep { color: #94a3b8; font-size: 13px; }

/* ── Header ─────────────────────────────────────────────────────── */
.dash-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}

.dash-header h2 {
  font-size: 22px;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 4px;
}

.dash-sub {
  font-size: 13px;
  color: #64748b;
  margin: 0;
}

.welcome-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 99px;
  padding: 6px 16px;
  font-size: 13px;
  color: #475569;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.welcome-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
  flex-shrink: 0;
}

/* ── Loading ────────────────────────────────────────────────────── */
.loading-state {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 60px 0;
  justify-content: center;
  color: #94a3b8;
  font-size: 14px;
}

.spinner {
  width: 22px;
  height: 22px;
  border: 2.5px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ── Empty / error state ────────────────────────────────────────── */
.dashboard-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 80px 24px;
  text-align: center;
}

.dashboard-empty-state h3 {
  font-size: 16px;
  font-weight: 700;
  color: #334155;
  margin: 0;
}

.dashboard-empty-state p {
  font-size: 13px;
  color: #94a3b8;
  margin: 0;
  max-width: 320px;
  line-height: 1.6;
}

.empty-btn {
  margin-top: 4px;
  padding: 8px 20px;
  background: #3b82f6;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}

.empty-btn:hover { background: #2563eb; }

/* ── KPI cards ──────────────────────────────────────────────────── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.kpi-card {
  background: #fff;
  border-radius: 14px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
  position: relative;
  overflow: hidden;
  transition: box-shadow 0.2s, transform 0.2s;
}

.kpi-card:hover {
  box-shadow: 0 6px 20px rgba(0,0,0,0.09);
  transform: translateY(-2px);
}

.kpi-icon-wrap {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kpi-body {
  flex: 1;
  min-width: 0;
}

.kpi-value {
  font-size: 28px;
  font-weight: 800;
  color: #0f172a;
  line-height: 1;
  margin-bottom: 3px;
}

.kpi-label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 2px;
}

.kpi-meta {
  font-size: 11px;
  color: #94a3b8;
}

.kpi-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  border-radius: 0 0 14px 14px;
}

/* ── Resolution rate ────────────────────────────────────────────── */
.rate-card {
  background: #fff;
  border-radius: 14px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  padding: 16px 20px;
  margin-bottom: 20px;
}

.rate-label {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #475569;
  margin-bottom: 8px;
}

.rate-label strong {
  color: #10b981;
  font-size: 15px;
}

.rate-track {
  height: 8px;
  background: #f1f5f9;
  border-radius: 99px;
  overflow: hidden;
  margin-bottom: 10px;
}

.rate-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #34d399);
  border-radius: 99px;
  transition: width 0.6s ease;
}

.rate-breakdown {
  display: flex;
  gap: 16px;
  font-size: 12px;
}

.rb-open   { color: #f59e0b; font-weight: 600; }
.rb-progress { color: #6366f1; font-weight: 600; }
.rb-closed { color: #10b981; font-weight: 600; }

/* ── Chart cards ────────────────────────────────────────────────── */
.charts-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.chart-card {
  background: #fff;
  border-radius: 14px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  overflow: hidden;
}

.chart-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 18px 20px 12px;
  border-bottom: 1px solid #f8fafc;
}

.chart-title {
  font-size: 14px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 2px;
}

.chart-subtitle {
  font-size: 12px;
  color: #94a3b8;
}

.chart-body {
  padding: 8px 16px 12px;
}

.chart-grouped-wrap {
  position: relative;
}

.bar-scroll-outer {
  position: relative;
}

@media (max-width: 640px) {
  .bar-scroll-outer {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  .bar-scroll-outer .bar-svg {
    width: 700px;
    height: auto;
  }
}

.bar-svg {
  width: 100%;
  height: auto;
  display: block;
}

/* ── Grouped chart legend ────────────────────────────────────────── */
.grouped-legend {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.gl-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
}

.gl-dot {
  width: 10px;
  height: 10px;
  border-radius: 3px;
  flex-shrink: 0;
}

/* ── Tooltip ─────────────────────────────────────────────────────── */
.bar-tooltip {
  position: absolute;
  pointer-events: none;
  background: #1e293b;
  border-radius: 10px;
  padding: 10px 14px;
  min-width: 140px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.18);
  z-index: 10;
}

.tt-month {
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 8px;
}

.tt-row {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  margin-bottom: 4px;
}

.tt-row:last-child { margin-bottom: 0; }

.tt-dot {
  width: 8px;
  height: 8px;
  border-radius: 2px;
  flex-shrink: 0;
}

.tt-label {
  flex: 1;
  color: #94a3b8;
}

.tt-val {
  font-weight: 700;
  color: #fff;
}

/* ── Donut chart ────────────────────────────────────────────────── */
.donut-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 16px 18px;
  position: relative;
}

.donut-svg {
  width: 160px;
  flex-shrink: 0;
}

.donut-legend {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px 4px;
  margin-top: 14px;
  width: 100%;
}

.donut-tooltip {
  position: absolute;
  pointer-events: none;
  background: #1e293b;
  border-radius: 10px;
  padding: 7px 12px;
  display: flex;
  align-items: center;
  gap: 7px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.18);
  z-index: 10;
  white-space: nowrap;
}

.dt-dot {
  width: 9px;
  height: 9px;
  border-radius: 3px;
  flex-shrink: 0;
}

.dt-cat {
  font-size: 12px;
  color: #94a3b8;
  flex: 1;
}

.dt-count {
  font-size: 13px;
  font-weight: 700;
  color: #fff;
}

.dt-pct {
  font-size: 11px;
  color: #64748b;
  margin-left: 2px;
}

.legend-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  background: #f8fafc;
  border-radius: 10px;
  padding: 8px 6px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 3px;
  flex-shrink: 0;
}

.legend-label {
  color: #64748b;
  font-size: 11px;
  text-align: center;
  white-space: nowrap;
}

.legend-count {
  font-weight: 800;
  color: #1e293b;
  font-size: 16px;
  line-height: 1;
}

/* ── Bottom row ─────────────────────────────────────────────────── */
.bottom-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

/* ── Calendar tooltip ───────────────────────────────────────────── */
.cal-body {
  position: relative;
}

.cal-tooltip {
  position: absolute;
  pointer-events: none;
  background: #1e293b;
  border-radius: 10px;
  padding: 9px 13px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.18);
  z-index: 10;
  min-width: 130px;
}

.cal-tt-date {
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 2px;
}

.cal-tt-total {
  font-size: 11px;
  color: #64748b;
  margin-bottom: 7px;
}

.cal-tt-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  margin-bottom: 3px;
}

.cal-tt-row:last-child { margin-bottom: 0; }

.cal-tt-dot {
  width: 8px;
  height: 8px;
  border-radius: 2px;
  flex-shrink: 0;
}

.cal-tt-cat {
  flex: 1;
  color: #94a3b8;
}

.cal-tt-cnt {
  font-weight: 700;
  color: #fff;
}

/* ── Calendar ───────────────────────────────────────────────────── */
.cal-nav {
  display: flex;
  gap: 4px;
}

.cal-btn {
  width: 28px;
  height: 28px;
  border: 1px solid #e2e8f0;
  border-radius: 7px;
  background: #f8fafc;
  color: #475569;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.15s;
}

.cal-btn:hover {
  background: #e2e8f0;
}

.cal-body {
  padding: 10px 16px;
}

.cal-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  margin-bottom: 6px;
}

.cal-wd {
  text-align: center;
  font-size: 11px;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  padding: 4px 0;
  letter-spacing: 0.3px;
}

.cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
}

.cal-day {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 5px 2px;
  border-radius: 8px;
  min-height: 44px;
  position: relative;
  transition: background 0.15s;
}

.cal-day:hover:not(.cal-other) {
  background: #f8fafc;
}

.cal-other .cal-num {
  color: #cbd5e1;
}

.cal-today {
  background: #eff6ff;
}

.cal-today .cal-num {
  color: #3b82f6;
  font-weight: 800;
}

.cal-num {
  font-size: 13px;
  color: #334155;
  font-weight: 500;
  line-height: 1;
}

.cal-badge {
  margin-top: 3px;
  background: #3b82f6;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  border-radius: 99px;
  min-width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}

.cal-legend {
  display: flex;
  gap: 16px;
  padding: 8px 16px 14px;
  border-top: 1px solid #f8fafc;
}

.cal-leg-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #94a3b8;
}

.cal-leg-dot {
  width: 10px;
  height: 10px;
  border-radius: 3px;
}

.cal-leg-today {
  width: 10px;
  height: 10px;
  border-radius: 3px;
  background: #eff6ff;
  border: 1.5px solid #3b82f6;
}

/* ── Recent reports ─────────────────────────────────────────────── */
.view-all-link {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  font-weight: 600;
  color: #3b82f6;
  text-decoration: none;
  transition: color 0.15s;
}

.view-all-link:hover {
  color: #2563eb;
}

.recent-list {
  padding: 4px 0;
}

.empty-recent {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 32px 0;
  color: #94a3b8;
  font-size: 13px;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 20px;
  border-bottom: 1px solid #f8fafc;
  transition: background 0.15s;
}

.recent-item:last-child {
  border-bottom: none;
}

.recent-item:hover {
  background: #fafafa;
}

.recent-cat-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.recent-info {
  flex: 1;
  min-width: 0;
}

.recent-cat {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.recent-loc {
  font-size: 11px;
  color: #94a3b8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.recent-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  flex-shrink: 0;
}

.status-chip {
  font-size: 10px;
  font-weight: 700;
  border-radius: 99px;
  padding: 2px 9px;
  white-space: nowrap;
}

.sc-open         { background: #fef3c7; color: #92400e; }
.sc-in-progress  { background: #e0e7ff; color: #3730a3; }
.sc-closed       { background: #dcfce7; color: #166534; }

.recent-date {
  font-size: 11px;
  color: #94a3b8;
}

/* ── Responsive ─────────────────────────────────────────────────── */
@media (max-width: 1100px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .charts-row { grid-template-columns: 1fr; }
  .bottom-row { grid-template-columns: 1fr; }
}

@media (max-width: 640px) {
  .dash { padding: 20px 16px; }
  .kpi-grid { grid-template-columns: 1fr 1fr; }
}
</style>
