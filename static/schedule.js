document.addEventListener("DOMContentLoaded", () => {
  renderSchedule();

  document.getElementById("scheduleForm").addEventListener("submit", e => {
    e.preventDefault();

    const day = day.value;
    const subject = document.getElementById("subject").value;
    const time = document.getElementById("time").value;

    const data = JSON.parse(localStorage.getItem("schedule") || "[]");
    data.push({ day, subject, time });
    localStorage.setItem("schedule", JSON.stringify(data));

    renderSchedule();
  });
});

function renderSchedule() {
  const list = document.getElementById("scheduleList");
  const data = JSON.parse(localStorage.getItem("schedule") || "[]");
  list.innerHTML = "";

  data.forEach((item, i) => {
    list.innerHTML += `
      <div>
        ${item.day} - ${item.subject} - ${item.time}
        <button onclick="removeItem(${i})">حذف</button>
      </div>`;
  });
}

function removeItem(i) {
  const data = JSON.parse(localStorage.getItem("schedule"));
  data.splice(i, 1);
  localStorage.setItem("schedule", JSON.stringify(data));
  renderSchedule();
}
