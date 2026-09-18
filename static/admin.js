const pending = Number(document.getElementById("pending").value);
const confirmed = Number(document.getElementById("confirmed").value);
const completed = Number(document.getElementById("completed").value);
const cancelled = Number(document.getElementById("cancelled").value);

const monthlyRevenue = JSON.parse(
    document.getElementById("monthlyRevenue").value
);

new Chart(document.getElementById("statusChart"), {
    type: "pie",
    data: {
        labels: ["Pending", "Confirmed", "Completed", "Cancelled"],
        datasets: [{
            data: [pending, confirmed, completed, cancelled],
            backgroundColor: ["#facc15", "#22c55e", "#3b82f6", "#ef4444"]
        }]
    }
});

new Chart(document.getElementById("revenueChart"), {
    type: "bar",
    data: {
        labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        datasets: [{
            label: "Revenue",
            data: monthlyRevenue,
            backgroundColor: "#2563eb"
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});