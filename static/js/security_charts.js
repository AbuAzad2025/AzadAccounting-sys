/**
 * ═══════════════════════════════════════════════════════════════════
 * 📊 رسوم بيانية للإحصائيات - Security Module Charts
 * ═══════════════════════════════════════════════════════════════════
 */

(function() {
  if (window.__SECURITY_CHARTS_INIT__) return;
  window.__SECURITY_CHARTS_INIT__ = true;
  'use strict';
  
  document.addEventListener('DOMContentLoaded', function() {
    if (typeof Chart === 'undefined') {
      return;
    }
    
    initUsersTrendChart();
    initFailedLoginsChart();
    initSystemHealthChart();
    initActivityChart();
  });
  
  /**
   * رسم بياني لنمو المستخدمين
   */
  function initUsersTrendChart() {
    const canvas = document.getElementById('usersTrendChart');
    if (!canvas) return;
    
    // بيانات آخر 7 أيام (محاكاة - يمكن جلبها من API)
    const last7Days = generateLast7Days();
    const usersData = generateUsersTrendData();
    
    new Chart(canvas, {
      type: 'line',
      data: {
        labels: last7Days,
        datasets: [{
          label: 'المستخدمين النشطين',
          data: usersData,
          borderColor: '#667eea',
          backgroundColor: 'rgba(102, 126, 234, 0.1)',
          tension: 0.4,
          fill: true,
          pointRadius: 3,
          pointHoverRadius: 5
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function(context) {
                return 'مستخدمين: ' + context.parsed.y;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { precision: 0 }
          }
        }
      }
    });
  }
  
  /**
   * رسم بياني لمحاولات الدخول الفاشلة
   */
  function initFailedLoginsChart() {
    const canvas = document.getElementById('failedLoginsChart');
    if (!canvas) return;
    
    const last7Days = generateLast7Days();
    const failedData = generateFailedLoginsData();
    
    new Chart(canvas, {
      type: 'bar',
      data: {
        labels: last7Days,
        datasets: [{
          label: 'محاولات فاشلة',
          data: failedData,
          backgroundColor: 'rgba(220, 53, 69, 0.7)',
          borderColor: '#dc3545',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { precision: 0 }
          }
        }
      }
    });
  }
  
  /**
   * رسم بياني لصحة النظام
   */
  function initSystemHealthChart() {
    const canvas = document.getElementById('systemHealthChart');
    if (!canvas) return;
    
    new Chart(canvas, {
      type: 'doughnut',
      data: {
        labels: ['نشط', 'محظور', 'معطل'],
        datasets: [{
          data: [
            parseInt(document.querySelector('[data-active-users]')?.dataset.activeUsers || 0),
            parseInt(document.querySelector('[data-blocked-users]')?.dataset.blockedUsers || 0),
            parseInt(document.querySelector('[data-inactive-users]')?.dataset.inactiveUsers || 0)
          ],
          backgroundColor: [
            'rgba(40, 167, 69, 0.8)',
            'rgba(220, 53, 69, 0.8)',
            'rgba(108, 117, 125, 0.8)'
          ],
          borderWidth: 2,
          borderColor: '#fff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { font: { size: 11 } }
          }
        }
      }
    });
  }
  
  /**
   * Sparkline للنشاط الأسبوعي
   */
  function initActivityChart() {
    const canvas = document.getElementById('activitySparkline');
    if (!canvas) return;
    
    const data = generateActivityData();
    
    new Chart(canvas, {
      type: 'line',
      data: {
        labels: generateLast7Days(),
        datasets: [{
          data: data,
          borderColor: '#28a745',
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { display: false },
          y: { display: false }
        },
        elements: {
          line: { borderWidth: 2 }
        }
      }
    });
  }
  
  // ═══ دوال مساعدة ═══
  
  function generateLast7Days() {
    const days = [];
    const today = new Date();
    
    for (let i = 6; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const day = date.toLocaleDateString('ar-EG', { weekday: 'short' });
      days.push(day);
    }
    
    return days;
  }
  
  function generateUsersTrendData() {
    // محاكاة بيانات - في الإنتاج، تُجلب من API
    const baseUsers = parseInt(document.querySelector('[data-total-users]')?.dataset.totalUsers || 45);
    const data = [];
    
    for (let i = 0; i < 7; i++) {
      const variance = Math.floor(Math.random() * 5) - 2;
      data.push(Math.max(0, baseUsers + variance - (6 - i)));
    }
    
    return data;
  }
  
  function generateFailedLoginsData() {
    // محاكاة بيانات - في الإنتاج، تُجلب من API
    const data = [];
    
    for (let i = 0; i < 7; i++) {
      data.push(Math.floor(Math.random() * 10));
    }
    
    return data;
  }
  
  function generateActivityData() {
    // محاكاة بيانات نشاط عام
    const data = [];
    
    for (let i = 0; i < 7; i++) {
      data.push(Math.floor(Math.random() * 50) + 20);
    }
    
    return data;
  }
  
  /**
   * API للحصول على بيانات حقيقية (للاستخدام المستقبلي)
   */
  async function fetchRealChartData() {
    try {
      const response = await fetch('/security/api/chart-data');
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
    }
    return null;
  }
  
})();

