<template>
  <div class="modules-page">
    <div class="page-header">
      <div>
        <h2>Safety Modules</h2>
        <p>Complete all modules to stay up to date with workplace safety standards.</p>
      </div>
      <div class="progress-summary">
        <span class="progress-label">Overall Progress</span>
        <div class="progress-bar-wrap">
          <div class="progress-bar" :style="{ width: overallProgress + '%' }"></div>
        </div>
        <span class="progress-pct">{{ overallProgress }}%</span>
      </div>
    </div>

    <div class="section-title">Videos</div>
    <div class="modules-grid">
      <div
        v-for="module in videoModules"
        :key="module.id"
        class="module-card"
        :class="{ completed: module.completed }"
      >
        <div class="card-thumb" :style="{ background: module.color }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="12" cy="12" r="10"/>
            <polygon points="10 8 16 12 10 16 10 8" fill="currentColor" stroke="none"/>
          </svg>
          <span v-if="module.completed" class="badge-done">Done</span>
        </div>
        <div class="card-body">
          <div class="card-category">{{ module.category }}</div>
          <div class="card-title">{{ module.title }}</div>
          <div class="card-meta">{{ module.duration }} &middot; {{ module.level }}</div>
        </div>
        <div class="card-footer">
          <button class="btn-start" :class="{ 'btn-review': module.completed }">
            {{ module.completed ? "Review" : "Watch" }}
          </button>
        </div>
      </div>
    </div>

    <div class="section-title" style="margin-top: 40px;">Guidelines</div>
    <div class="modules-grid">
      <div
        v-for="guide in guidelines"
        :key="guide.id"
        class="module-card"
        :class="{ completed: guide.completed }"
      >
        <div class="card-thumb" :style="{ background: guide.color }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="9" y1="13" x2="15" y2="13"/>
            <line x1="9" y1="17" x2="15" y2="17"/>
          </svg>
          <span v-if="guide.completed" class="badge-done">Done</span>
        </div>
        <div class="card-body">
          <div class="card-category">{{ guide.category }}</div>
          <div class="card-title">{{ guide.title }}</div>
          <div class="card-meta">{{ guide.pages }} pages &middot; {{ guide.level }}</div>
        </div>
        <div class="card-footer">
          <button class="btn-start" :class="{ 'btn-review': guide.completed }">
            {{ guide.completed ? "Review" : "Read" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const videoModules = [
  { id: 1, title: "Fire Safety & Evacuation Procedures", category: "Fire Safety", duration: "12 min", level: "Required", color: "linear-gradient(135deg,#ef4444,#b91c1c)", completed: false },
  { id: 2, title: "Personal Protective Equipment (PPE)", category: "PPE", duration: "8 min", level: "Required", color: "linear-gradient(135deg,#f59e0b,#d97706)", completed: false },
  { id: 3, title: "Emergency Response & First Aid", category: "Emergency", duration: "15 min", level: "Required", color: "linear-gradient(135deg,#10b981,#059669)", completed: false },
  { id: 4, title: "Chemical Handling & Hazmat Safety", category: "Hazmat", duration: "18 min", level: "Advanced", color: "linear-gradient(135deg,#8b5cf6,#7c3aed)", completed: false },
  { id: 5, title: "Working at Heights", category: "Fall Prevention", duration: "10 min", level: "Required", color: "linear-gradient(135deg,#3b82f6,#2563eb)", completed: false },
  { id: 6, title: "Electrical Safety Basics", category: "Electrical", duration: "9 min", level: "Required", color: "linear-gradient(135deg,#f97316,#ea580c)", completed: false },
];

const guidelines = [
  { id: 1, title: "Fire Safety Handbook", category: "Fire Safety", pages: 24, level: "Required", color: "linear-gradient(135deg,#ef4444,#b91c1c)", completed: false },
  { id: 2, title: "PPE Selection & Usage Guide", category: "PPE", pages: 18, level: "Required", color: "linear-gradient(135deg,#f59e0b,#d97706)", completed: false },
  { id: 3, title: "Emergency Contact & Procedures", category: "Emergency", pages: 8, level: "Required", color: "linear-gradient(135deg,#10b981,#059669)", completed: false },
  { id: 4, title: "Chemical Safety Data Sheets (SDS)", category: "Hazmat", pages: 32, level: "Advanced", color: "linear-gradient(135deg,#8b5cf6,#7c3aed)", completed: false },
  { id: 5, title: "Incident Reporting Guide", category: "Compliance", pages: 12, level: "Required", color: "linear-gradient(135deg,#06b6d4,#0891b2)", completed: false },
  { id: 6, title: "Lockout/Tagout (LOTO) Procedures", category: "Electrical", pages: 16, level: "Advanced", color: "linear-gradient(135deg,#f97316,#ea580c)", completed: false },
];

const allModules = [...videoModules, ...guidelines];
const overallProgress = computed(() => {
  const done = allModules.filter((m) => m.completed).length;
  return Math.round((done / allModules.length) * 100);
});
</script>

<style scoped>
.modules-page {
  padding: 28px 32px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 32px;
  gap: 24px;
  flex-wrap: wrap;
}

.page-header h2 {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 6px;
}

.page-header p {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.progress-summary {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.progress-label {
  font-size: 13px;
  color: #64748b;
  white-space: nowrap;
}

.progress-bar-wrap {
  width: 140px;
  height: 8px;
  background: #e5e7eb;
  border-radius: 99px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: #3b82f6;
  border-radius: 99px;
  transition: width 0.4s;
}

.progress-pct {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
  min-width: 32px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e5e7eb;
}

.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 18px;
}

.module-card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: box-shadow 0.2s, transform 0.2s;
}

.module-card:hover {
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.module-card.completed {
  opacity: 0.75;
}

.card-thumb {
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  color: rgba(255,255,255,0.85);
}

.card-thumb svg {
  width: 40px;
  height: 40px;
}

.badge-done {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0,0,0,0.35);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 99px;
}

.card-body {
  padding: 14px 16px 8px;
  flex: 1;
}

.card-category {
  font-size: 11px;
  font-weight: 600;
  color: #3b82f6;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.4;
  margin-bottom: 6px;
}

.card-meta {
  font-size: 12px;
  color: #94a3b8;
}

.card-footer {
  padding: 10px 16px 14px;
}

.btn-start {
  width: 100%;
  padding: 8px;
  background: #3b82f6;
  color: #fff;
  border: none;
  border-radius: 7px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-start:hover {
  background: #2563eb;
}

.btn-review {
  background: #e5e7eb;
  color: #374151;
}

.btn-review:hover {
  background: #d1d5db;
}
</style>
