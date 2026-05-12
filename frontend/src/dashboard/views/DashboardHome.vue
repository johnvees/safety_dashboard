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
      <span>Loading dashboard…</span>
    </div>

    <template v-else>
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
        <!-- Monthly bar chart -->
        <div class="chart-card chart-wide">
          <div class="chart-header">
            <div>
              <div class="chart-title">Monthly Trend</div>
              <div class="chart-subtitle">Reports filed per month (last 6 months)</div>
            </div>
          </div>
          <div class="chart-body">
            <svg viewBox="0 0 520 185" class="bar-svg" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#3b82f6"/>
                  <stop offset="100%" stop-color="#bfdbfe"/>
                </linearGradient>
                <linearGradient id="barGradHov" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#2563eb"/>
                  <stop offset="100%" stop-color="#93c5fd"/>
                </linearGradient>
              </defs>
              <!-- Horizontal grid lines -->
              <line v-for="gl in gridLines" :key="gl.y"
                x1="44" :y1="gl.y" x2="512" :y2="gl.y"
                stroke="#f1f5f9" stroke-width="1.5"/>
              <!-- Y-axis labels -->
              <text v-for="gl in gridLines" :key="`y${gl.y}`"
                x="38" :y="gl.y + 4"
                text-anchor="end" font-size="10" fill="#94a3b8">{{ gl.label }}</text>
              <!-- Bars -->
              <g v-for="(bar, i) in barData" :key="i">
                <rect
                  :x="bar.x" :y="bar.y" :width="bar.w" :height="Math.max(bar.h, 2)"
                  rx="5"
                  :fill="bar.h > 0 ? 'url(#barGrad)' : '#f1f5f9'"
                />
                <text v-if="bar.count > 0"
                  :x="bar.x + bar.w / 2" :y="bar.y - 7"
                  text-anchor="middle" font-size="11" font-weight="700" fill="#3b82f6">
                  {{ bar.count }}
                </text>
                <!-- Month label -->
                <text
                  :x="bar.x + bar.w / 2" :y="175"
                  text-anchor="middle" font-size="11" fill="#64748b">
                  {{ bar.label }}
                </text>
              </g>
            </svg>
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
          <div class="donut-body">
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
              />
              <text x="100" y="95" text-anchor="middle" font-size="26" font-weight="800" fill="#1e293b">{{ stats.total }}</text>
              <text x="100" y="113" text-anchor="middle" font-size="10" fill="#94a3b8" letter-spacing="1">REPORTS</text>
            </svg>
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
          <div class="cal-body">
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
              >
                <span class="cal-num">{{ day.date }}</span>
                <span v-if="day.count > 0 && day.currentMonth" class="cal-badge" :title="`${day.count} report(s)`">{{ day.count }}</span>
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
            <div v-for="rec in recentRecords" :key="rec.id" class="recent-item">
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
import { ref, computed, onMounted } from 'vue';
import { inspectionK3LService } from '@/services/inspectionK3LService.js';
import { authService } from '@/services/authService.js';

const records = ref([]);
const loading = ref(true);
const calendarDate = ref(new Date());

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
  total: records.value.length,
  open: records.value.filter(r => r.status === 'Open').length,
  inProgress: records.value.filter(r => r.status === 'In Progress').length,
  closed: records.value.filter(r => r.status === 'Closed').length,
}));

const resolutionRate = computed(() => {
  if (!stats.value.total) return 0;
  return Math.round((stats.value.closed / stats.value.total) * 100);
});

// ── Bar chart ──────────────────────────────────────────────────────
const monthlyData = computed(() => {
  const now = new Date();
  const months = Array.from({ length: 6 }, (_, i) => {
    const d = new Date(now.getFullYear(), now.getMonth() - (5 - i), 1);
    return { label: d.toLocaleString('default', { month: 'short' }), year: d.getFullYear(), month: d.getMonth(), count: 0 };
  });
  records.value.forEach(r => {
    if (!r.tanggal) return;
    const d = new Date(r.tanggal);
    const idx = months.findIndex(m => m.year === d.getFullYear() && m.month === d.getMonth());
    if (idx >= 0) months[idx].count++;
  });
  return months;
});

const BAR_W = 54;
const BAR_GAP = 22;
const CHART_TOP = 15;
const CHART_H = 140;
const CHART_LEFT = 48;

const barData = computed(() => {
  const data = monthlyData.value;
  const maxCount = Math.max(...data.map(d => d.count), 1);
  return data.map((d, i) => {
    const h = (d.count / maxCount) * CHART_H;
    return {
      x: CHART_LEFT + i * (BAR_W + BAR_GAP),
      y: CHART_TOP + CHART_H - h,
      w: BAR_W,
      h,
      label: d.label,
      count: d.count,
    };
  });
});

const gridLines = computed(() => {
  const maxCount = Math.max(...monthlyData.value.map(d => d.count), 1);
  return [0, 1, 2, 3, 4].map(i => ({
    y: CHART_TOP + CHART_H - (i / 4) * CHART_H,
    label: Math.round((i / 4) * maxCount),
  }));
});

// ── Donut chart ────────────────────────────────────────────────────
const CAT_COLORS = {
  'Unsafe Action':    '#ef4444',
  'Unsafe Condition': '#f59e0b',
  'Lingkungan':       '#10b981',
  'Kesehatan Kerja':  '#3b82f6',
  'APD':              '#8b5cf6',
  'Housekeeping':     '#06b6d4',
  'Lainnya':          '#94a3b8',
};

function categoryColor(cat) {
  return CAT_COLORS[cat] || '#94a3b8';
}

const CIRC = 2 * Math.PI * 65;

const donutSegments = computed(() => {
  if (!stats.value.total) return [];
  const counts = {};
  records.value.forEach(r => { counts[r.kategoriTemuan] = (counts[r.kategoriTemuan] || 0) + 1; });
  let cumulative = 0;
  return Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
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
      reportMap[d.getDate()] = (reportMap[d.getDate()] || 0) + 1;
    }
  });

  const days = [];
  for (let i = firstDow - 1; i >= 0; i--) days.push({ date: daysInPrev - i, currentMonth: false, isToday: false, count: 0 });
  for (let d = 1; d <= daysInMonth; d++) {
    const isToday = d === today.getDate() && month === today.getMonth() && year === today.getFullYear();
    days.push({ date: d, currentMonth: true, isToday, count: reportMap[d] || 0 });
  }
  for (let d = 1; days.length < 42; d++) days.push({ date: d, currentMonth: false, isToday: false, count: 0 });
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
  [...records.value]
    .sort((a, b) => new Date(b.createdAt || 0) - new Date(a.createdAt || 0))
    .slice(0, 6)
);

function formatDate(s) {
  if (!s) return '—';
  return new Date(s + 'T00:00:00').toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
}

onMounted(async () => {
  try {
    records.value = await inspectionK3LService.list();
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.dash {
  padding: 28px 32px;
  max-width: 1400px;
}

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

.bar-svg {
  width: 100%;
  height: auto;
  display: block;
}

/* ── Donut chart ────────────────────────────────────────────────── */
.donut-body {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px 18px;
}

.donut-svg {
  width: 140px;
  flex-shrink: 0;
}

.donut-legend {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 3px;
  flex-shrink: 0;
}

.legend-label {
  flex: 1;
  color: #475569;
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.legend-count {
  font-weight: 700;
  color: #1e293b;
  font-size: 12px;
}

/* ── Bottom row ─────────────────────────────────────────────────── */
.bottom-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
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
