// schedule.js (محسّن ومرتب)

// استمع لحدث DOM جاهز ثم ربط الفورم وتحميل البيانات المخزنة
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('scheduleForm');
  const list = document.getElementById('scheduleList');

  // تحميل وعرض الجدول عند بدء الصفحة
  renderSchedule();

  // عند إرسال الفورم: أضف الحصة واحفظها
  form.addEventListener('submit', function (e) {
    e.preventDefault();

    const dayEl = document.getElementById('day');
    const subjectEl = document.getElementById('subject');
    const timeEl = document.getElementById('time');

    const day = dayEl.value;
    const subject = subjectEl.value.trim();
    const time = timeEl.value.trim();

    if (!day) {
      alert('اختر اليوم');
      return;
    }
    if (!subject) {
      alert('اكتب اسم المادة');
      return;
    }
    if (!time) {
      alert('حدد الوقت');
      return;
    }

    const schedule = getSchedule();
    schedule.push({ day, subject, time });
    saveSchedule(schedule);

    // إعادة عرض وتفريغ الحقول
    renderSchedule();
    subjectEl.value = '';
    timeEl.value = '';
    dayEl.selectedIndex = 0; // يرجع للخيار الافتراضي
  });

  // حذف باستخدام التفويض: أي زر حذف داخل القائمة
  list.addEventListener('click', function (e) {
    if (e.target && e.target.matches('button.delete-btn')) {
      const idx = parseInt(e.target.dataset.index, 10);
      if (!Number.isNaN(idx)) {
        deleteClass(idx);
      }
    }
  });
});


// ------------------------------------------------------------------
// دوال التخزين في localStorage
// ------------------------------------------------------------------
function getSchedule() {
  try {
    return JSON.parse(localStorage.getItem('study_schedule')) || [];
  } catch (err) {
    console.error('خطأ بقراءة localStorage:', err);
    return [];
  }
}

function saveSchedule(data) {
  try {
    localStorage.setItem('study_schedule', JSON.stringify(data));
  } catch (err) {
    console.error('خطأ بحفظ localStorage:', err);
    alert('تعذر حفظ البيانات محلياً');
  }
}


// ------------------------------------------------------------------
// عرض الجدول في الصفحة
// ------------------------------------------------------------------
function renderSchedule() {
  const list = document.getElementById('scheduleList');
  const schedule = getSchedule();

  list.innerHTML = '';

  if (schedule.length === 0) {
    list.innerHTML =
      '<div style="text-align:center; color:#666; padding:8px">لا يوجد حصص بعد</div>';
    return;
  }

  schedule.forEach((item, index) => {
    const row = document.createElement('div');
    row.className = 'item';

    row.innerHTML = `
      <span>${escapeHtml(item.day)}</span>
      <span>${escapeHtml(item.subject)}</span>
      <span>${escapeHtml(item.time)}</span>
      <button class="delete-btn" data-index="${index}">حذف</button>
    `;

    list.appendChild(row);
  });
}



// ------------------------------------------------------------------
// حذف عنصر من الجدول
// ------------------------------------------------------------------
function deleteClass(index) {
  if (!confirm('هل تريد حذف هذه الحصة؟')) return;

  const schedule = getSchedule();
  if (index < 0 || index >= schedule.length) return;

  schedule.splice(index, 1);
  saveSchedule(schedule);
  renderSchedule();
}


// ------------------------------------------------------------------
// مساعدة: حماية بسيطة من HTML injection عند عرض النصوص
// ------------------------------------------------------------------
function escapeHtml(unsafe) {
  return String(unsafe)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}